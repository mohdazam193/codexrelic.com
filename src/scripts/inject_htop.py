"""
inject_htop.py — Adds the HTOP right-sidebar widget to all pages that don't already have it.
Wraps existing content in a dashboard-layout flex container.
"""
import re
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PUBLIC_DIR = os.path.join(BASE_DIR, "public")

# Pages that need the widget injected (index.html already has it)
TARGET_PAGES = [
    "about.html",
    "resume.html",
    "projects.html",
    "blog.html",
    "tech-news.html",
    "tools.html",
    "movies.html",
    "community.html",
    "contact.html",
]

RIGHT_SIDEBAR_HTML = """
    <!-- ═══ RIGHT SIDEBAR (BIFURCATION) ══════════════════ -->
    <aside class="right-sidebar">
      <!-- ═══ LIVE VM STATS WIDGET ════════════════════════ -->
      <div id="vm-stats-widget" class="vm-stats-widget" aria-label="Live VM Statistics">
        <div class="vm-widget-header">
          <span class="vm-widget-title">htop - Live VM</span>
      <div class="htop-history-tabs" style="display:flex;gap:4px;margin-right:auto;margin-left:12px;">
        <button class="htop-tab active">Live</button>
      </div>
          <span class="bento-status status-green" id="vm-connection-status">WS CON</span>
        </div>
        <div class="vm-widget-body">
          <div id="vm-cpu-container" class="vm-stat-section">
            <!-- CPU bars will be injected here -->
          </div>
          <div class="vm-stat-section">
            <div class="vm-stat-row">
              <span class="vm-stat-label">Mem[</span>
              <div class="vm-bar-track">
                <div id="vm-mem-bar" class="vm-bar-fill" style="width:0%; background:var(--c-accent)"></div>
              </div>
              <span id="vm-mem-text" class="vm-stat-value">0G/0G]</span>
            </div>
            <div class="vm-stat-row">
              <span class="vm-stat-label">Swp[</span>
              <div class="vm-bar-track">
                <div id="vm-swp-bar" class="vm-bar-fill" style="width:0%; background:var(--c-red)"></div>
              </div>
              <span id="vm-swp-text" class="vm-stat-value">0K/0K]</span>
            </div>
          </div>
          <div class="vm-stat-text-group">
            <div class="vm-stat-text-row">
              <span class="vm-text-label">Tasks:</span>
              <span id="vm-tasks-text" class="vm-text-val">0, 0 running</span>
            </div>
            <div class="vm-stat-text-row">
              <span class="vm-text-label">Load average:</span>
              <span id="vm-load-text" class="vm-text-val">0.00 0.00 0.00</span>
            </div>
            <div class="vm-stat-text-row">
              <span class="vm-text-label">Uptime:</span>
              <span id="vm-uptime-text" class="vm-text-val">0 days, 00:00:00</span>
            </div>
          </div>
        </div>
      </div>
    </aside>"""


for filename in TARGET_PAGES:
    filepath = os.path.join(PUBLIC_DIR, filename)
    if not os.path.exists(filepath):
        print(f"[⚠️] Skipping {filename} — file not found")
        continue

    with open(filepath, "r") as f:
        content = f.read()

    # Skip if already has the widget
    if "vm-stats-widget" in content:
        print(f"[⏭️] Skipping {filename} — already has HTOP widget")
        continue

    # Pattern: find <main class="main"...> ... <div class="content-wrap">
    # We need to wrap the content-wrap in a dashboard-layout div and add the right sidebar
    
    # Step 1: Wrap content-wrap inside a dashboard-layout div
    # Find: <main class="main"...>\n    <div class="content-wrap">
    # Replace with: <main class="main"...>\n    <div class="dashboard-layout">\n      <div class="content-wrap">
    
    main_pattern = re.compile(
        r'(<main class="main"[^>]*>)\s*\n(\s*<div class="content-wrap">)',
        re.DOTALL
    )
    
    match = main_pattern.search(content)
    if not match:
        print(f"[⚠️] Skipping {filename} — could not find main+content-wrap pattern")
        continue

    # Step 2: Find the closing </div> for content-wrap and </main>
    # We need to insert the right-sidebar before </main>
    
    # Find </main> and insert dashboard-layout wrapper + right sidebar before it
    main_close_pattern = re.compile(r'(</div>\s*)\n(\s*</main>)')
    
    # First, add the dashboard-layout wrapper opening
    content = main_pattern.sub(
        r'\1\n    <div class="dashboard-layout">\n\2',
        content
    )
    
    # Now find </main> and insert closing </div> for dashboard-layout + right sidebar
    # The pattern is: last </div> before </main>
    # We need to add: </div> (close content-wrap) + right-sidebar + </div> (close dashboard-layout)
    # But content-wrap's </div> should already be there, so we just need to add right-sidebar + </div> before </main>
    
    content = content.replace(
        '</main>',
        RIGHT_SIDEBAR_HTML + '\n    </div>\n  </main>',
        1  # only first occurrence
    )
    
    with open(filepath, "w") as f:
        f.write(content)
    
    print(f"[✅] Injected HTOP widget into {filename}")

print("\n✅ Done! All pages now have the HTOP widget.")
