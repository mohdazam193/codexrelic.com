import os
import re

html_files = [
    "index.html",
    "about.html",
    "resume.html",
    "projects.html",
    "blog.html",
    "movies.html",
    "community.html",
    "contact.html"
]

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Master navigation items list
nav_items = [
    {"href": "index.html", "label": "Home", "icon": '<svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/></svg>'},
    {"href": "about.html", "label": "About", "icon": '<svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>'},
    {"href": "resume.html", "label": "Resume", "icon": '<svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/></svg>'},
    {"href": "projects.html", "label": "Projects", "icon": '<svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/></svg>'},
    {"href": "blog.html", "label": "Blog", "icon": '<svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"/><path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"/></svg>'},
    {"href": "movies.html", "label": "Movies", "icon": '<svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="2" width="20" height="20" rx="2.18" ry="2.18"/><line x1="7" y1="2" x2="7" y2="22"/><line x1="17" y1="2" x2="17" y2="22"/><line x1="2" y1="12" x2="22" y2="12"/><line x1="2" y1="7" x2="7" y2="7"/><line x1="2" y1="17" x2="7" y2="17"/><line x1="17" y1="17" x2="22" y2="17"/><line x1="17" y1="7" x2="22" y2="7"/></svg>'}
]

community_items = [
    {"href": "community.html", "label": "Community", "icon": '<svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>'},
    {"href": "contact.html", "label": "Contact", "icon": '<svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/><polyline points="22,6 12,13 2,6"/></svg>'}
]

# Mobile navigation items list
mobile_nav_items = [
    {"href": "index.html", "label": "Home", "icon": '<svg class="mobile-nav-item-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/></svg>'},
    {"href": "about.html", "label": "About", "icon": '<svg class="mobile-nav-item-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>'},
    {"href": "resume.html", "label": "Resume", "icon": '<svg class="mobile-nav-item-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>'},
    {"href": "blog.html", "label": "Blog", "icon": '<svg class="mobile-nav-item-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"/><path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"/></svg>'},
    {"href": "movies.html", "label": "Movies", "icon": '<svg class="mobile-nav-item-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="2" width="20" height="20" rx="2.18" ry="2.18"/><line x1="7" y1="2" x2="7" y2="22"/><line x1="17" y1="2" x2="17" y2="22"/><line x1="2" y1="12" x2="22" y2="12"/></svg>'}
]

def build_sidebar_html(filename):
    lines = []
    lines.append('  <aside class="sidebar" aria-label="Main navigation">')
    lines.append('    <a class="sidebar-brand" href="index.html">')
    lines.append('      <img src="assets/images/logo-dark.png" style="height:24px;object-fit:contain" alt="Logo">')
    lines.append('    </a>\n')
    lines.append('    <nav class="nav" role="navigation">')
    lines.append('      <span class="nav-group-label">Navigation</span>\n')
    
    for item in nav_items:
        is_active = item["href"] == filename
        active_str = ' class="nav-link active" aria-current="page"' if is_active else ' class="nav-link"'
        lines.append(f'      <a href="{item["href"]}"{active_str}>')
        lines.append(f'        {item["icon"]}')
        lines.append(f'        {item["label"]}')
        lines.append('      </a>')
        
    lines.append('\n      <div class="nav-sep"></div>')
    lines.append('      <span class="nav-group-label">Community</span>\n')
    
    for item in community_items:
        is_active = item["href"] == filename
        active_str = ' class="nav-link active" aria-current="page"' if is_active else ' class="nav-link"'
        lines.append(f'      <a href="{item["href"]}"{active_str}>')
        lines.append(f'        {item["icon"]}')
        lines.append(f'        {item["label"]}')
        lines.append('      </a>')
        
    lines.append('    </nav>\n')
    lines.append('    <div class="sidebar-footer">')
    lines.append('      <span class="palette-selector-label">Theme Accent</span>')
    lines.append('      <div class="palette-selector" aria-label="Choose color palette">')
    lines.append('        <button class="palette-swatch" data-palette="default" style="background:#5dd1c5" title="Default Teal"></button>')
    lines.append('        <button class="palette-swatch" data-palette="cyber" style="background:#10b981" title="Cyber Emerald"></button>')
    lines.append('        <button class="palette-swatch" data-palette="cosmic" style="background:#8b5cf6" title="Cosmic Violet"></button>')
    lines.append('        <button class="palette-swatch" data-palette="codex" style="background:#f59e0b" title="Ancient Codex"></button>')
    lines.append('        <button class="palette-swatch" data-palette="steel" style="background:#3b82f6" title="Steel SRE"></button>')
    lines.append('      </div>\n')
    lines.append('      <div class="sidebar-status">')
    lines.append('        <span class="status-dot" aria-hidden="true"></span>')
    lines.append('        Available · Hyderabad, IN')
    lines.append('      </div>')
    lines.append('      <div class="sidebar-socials">')
    lines.append('        <a class="social-btn" href="https://linkedin.com/in/mohdazam193" target="_blank" rel="noopener" title="LinkedIn">in</a>')
    lines.append('        <a class="social-btn" href="https://github.com/mohdazam193" target="_blank" rel="noopener" title="GitHub">gh</a>')
    lines.append('        <a class="social-btn" href="mailto:aazam.mohammad193@gmail.com" title="Email">@</a>')
    lines.append('      </div>')
    lines.append('      <button class="theme-toggle" id="theme-toggle" aria-label="Toggle colour theme">')
    lines.append('        <svg class="toggle-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>')
    lines.append('        <span class="toggle-label">Light mode</span>')
    lines.append('      </button>')
    lines.append('    </div>')
    lines.append('  </aside>')
    return '\n'.join(lines)

def build_mobile_nav_html(filename):
    lines = []
    lines.append('  <nav class="mobile-nav" aria-label="Mobile navigation">')
    lines.append('    <div class="mobile-nav-items">')
    
    for item in mobile_nav_items:
        is_active = item["href"] == filename
        active_str = ' class="mobile-nav-item active" aria-current="page"' if is_active else ' class="mobile-nav-item"'
        lines.append(f'      <a href="{item["href"]}"{active_str}>')
        lines.append(f'        {item["icon"]}')
        lines.append(f'        {item["label"]}')
        lines.append('      </a>')
        
    lines.append('    </div>')
    lines.append('  </nav>')
    return '\n'.join(lines)

combined_script = """  <script>
    (function(){
      var t=localStorage.getItem('cr-theme')||
        (window.matchMedia('(prefers-color-scheme: dark)').matches?'dark':'light');
      document.documentElement.setAttribute('data-theme',t);
      var p=localStorage.getItem('cr-palette')||'default';
      document.documentElement.setAttribute('data-palette',p);
    })();
  </script>"""

for filename in html_files:
    filepath = os.path.join(base_dir, "public", filename)
    if not os.path.exists(filepath):
        continue
        
    with open(filepath, 'r') as f:
        content = f.read()
        
    # Replace head theme script block
    head_script_pattern = re.compile(r'<script>\s*\(function\(\)\{\s*var t=localStorage\.getItem\(\'cr-theme\'\).*?\}\)\(\);\s*</script>', re.DOTALL)
    if head_script_pattern.search(content):
        content = head_script_pattern.sub(combined_script, content)
    else:
        # Try to find a script element that sets data-theme
        generic_head_pattern = re.compile(r'<script>.*?document\.documentElement\.setAttribute\(\'data-theme\'.*?</script>', re.DOTALL)
        if generic_head_pattern.search(content):
            content = generic_head_pattern.sub(combined_script, content)

    # Replace Sidebar
    sidebar_pattern = re.compile(r'<!--\s*═══\s*SIDEBAR\s*═══*.*?-->.*?<aside.*?>.*?</aside>', re.DOTALL)
    new_sidebar = "<!-- ═══ SIDEBAR ════════════════════════════════════ -->\n" + build_sidebar_html(filename)
    
    if sidebar_pattern.search(content):
        content = sidebar_pattern.sub(new_sidebar, content)
    else:
        sidebar_simple = re.compile(r'<aside class="sidebar".*?>.*?</aside>', re.DOTALL)
        content = sidebar_simple.sub(build_sidebar_html(filename), content)
        
    # Replace Mobile Nav
    mobile_pattern = re.compile(r'<!--\s*═══\s*MOBILE\s*NAV\s*═══*.*?-->.*?<nav class="mobile-nav".*?>.*?</nav>', re.DOTALL)
    new_mobile = "<!-- ═══ MOBILE NAV ══════════════════════════════════ -->\n" + build_mobile_nav_html(filename)
    
    if mobile_pattern.search(content):
        content = mobile_pattern.sub(new_mobile, content)
    else:
        mobile_simple = re.compile(r'<nav class="mobile-nav".*?>.*?</nav>', re.DOTALL)
        if mobile_simple.search(content):
            content = mobile_simple.sub(build_mobile_nav_html(filename), content)
        else:
            body_parts = content.split("</div>\n<script")
            if len(body_parts) == 2:
                body_parts[0] = body_parts[0] + "\n\n" + new_mobile + "\n"
                content = "</div>\n<script".join(body_parts)
            else:
                body_parts = content.split("</div>\n\n<script")
                if len(body_parts) == 2:
                    body_parts[0] = body_parts[0] + "\n\n" + new_mobile + "\n"
                    content = "</div>\n\n<script".join(body_parts)
                    
    with open(filepath, 'w') as f:
        f.write(content)
        
    print(f"[✅] Fully updated themes and palette selector in {filename}")
