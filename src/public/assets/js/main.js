/* ============================================================
   CODEXRELIC.COM — SRE & PLATFORM COMMAND ENGINE v3.0
   Interactive Shell, Live Telemetry, Topology Explorer & Command Palette
   ============================================================ */

/* ── 0. Immediate Theme Setup ── */
(function () {
  const stored = localStorage.getItem('cr-theme');
  const preferred = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
  document.documentElement.setAttribute('data-theme', stored || preferred);
})();

document.addEventListener('DOMContentLoaded', () => {

  /* ── 1. Audio Haptic Synthesizer ── */
  let audioCtx = null;
  function playClick(freq = 650, dur = 0.025) {
    try {
      if (!audioCtx) {
        const AudioContext = window.AudioContext || window.webkitAudioContext;
        if (AudioContext) audioCtx = new AudioContext();
      }
      if (audioCtx && audioCtx.state === 'running') {
        const osc = audioCtx.createOscillator();
        const gain = audioCtx.createGain();
        osc.frequency.setValueAtTime(freq, audioCtx.currentTime);
        gain.gain.setValueAtTime(0.03, audioCtx.currentTime);
        gain.gain.exponentialRampToValueAtTime(0.001, audioCtx.currentTime + dur);
        osc.connect(gain);
        gain.connect(audioCtx.destination);
        osc.start();
        osc.stop(audioCtx.currentTime + dur);
      }
    } catch (e) {}
  }

  window.addEventListener('click', () => {
    if (audioCtx && audioCtx.state === 'suspended') audioCtx.resume();
  }, { once: true });

  /* ── 2. Real-Time Dual Clocks (UTC & IST) ── */
  const clockUtc = document.getElementById('clock-utc');
  const clockIst = document.getElementById('clock-ist');

  function updateClocks() {
    const now = new Date();
    if (clockUtc) {
      const utcStr = now.toISOString().substring(11, 19);
      clockUtc.textContent = `UTC ${utcStr}`;
    }
    if (clockIst) {
      const istStr = now.toLocaleTimeString('en-US', {
        timeZone: 'Asia/Kolkata',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
        hour12: false
      });
      clockIst.textContent = `IST ${istStr}`;
    }
  }
  updateClocks();
  setInterval(updateClocks, 1000);

  /* ── 3. Theme Toggle & Logo Sync ── */
  const themeBtn = document.getElementById('theme-toggle');
  const root = document.documentElement;

  function setTheme(theme) {
    root.setAttribute('data-theme', theme);
    localStorage.setItem('cr-theme', theme);
    
    if (themeBtn) {
      themeBtn.innerHTML = theme === 'dark' 
        ? `<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="5"/><line x1="12" y1="1" x2="12" y2="3"/><line x1="12" y1="21" x2="12" y2="23"/><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/><line x1="1" y1="12" x2="3" y2="12"/><line x1="21" y1="12" x2="23" y2="12"/><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/></svg>`
        : `<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>`;
    }

    document.querySelectorAll('img.brand-logo, .sidebar-logo, .footer-logo, img[alt="CodexRelic"], img[alt="CODEXRELIC"]').forEach(img => {
      const src = img.getAttribute('src');
      if (src) {
        const baseDir = src.substring(0, src.lastIndexOf('/') + 1) || 'assets/images/';
        img.setAttribute('src', `${baseDir}logo-${theme}.svg`);
      }
    });
  }

  if (themeBtn) {
    themeBtn.addEventListener('click', () => {
      playClick(800, 0.03);
      const cur = root.getAttribute('data-theme') || 'dark';
      setTheme(cur === 'dark' ? 'light' : 'dark');
    });
    setTheme(root.getAttribute('data-theme') || 'dark');
  }

  /* ── 4. Active Navigation Sync ── */
  const currentPath = window.location.pathname.split('/').pop() || 'index.html';
  document.querySelectorAll('.nav-link-btn, .mobile-dock-btn').forEach(link => {
    const href = (link.getAttribute('href') || '').split('/').pop();
    if (href === currentPath || (currentPath === '' && href === 'index.html')) {
      link.classList.add('active');
    } else {
      link.classList.remove('active');
    }
  });

  /* ── 5. Interactive Cluster Topology Explorer ── */
  const topoNodes = document.querySelectorAll('.topo-node');
  const topoDetailBox = document.getElementById('topo-inspector-content');

  const TOPOLOGY_DETAILS = {
    'ingress': `<strong>[NODE: INGRESS EDGE ROUTER]</strong><br>
Type: Dual HAProxy Load Balancer (Active-Passive VRRP)<br>
TLS Termination: TLS 1.3 Strict · ECDSA secp384r1 · HTTP/2 + gRPC Enabled<br>
SLO: p99 Latency &lt; 8ms · 0.0001% Ingress Error Rate · Auto-heal active`,

    'traefik': `<strong>[NODE: IN-CLUSTER INGRESS CONTROLLER]</strong><br>
Type: Traefik v3.0 on Kubernetes (DaemonSet on Edge Nodes)<br>
Features: Automated ACME Let's Encrypt HTTP-01 Challenges · Rate-Limiting Middleware<br>
Routing: 4 Namespaces (prod, stage, uat, observability) with zero-downtime hot reload`,

    'k8s-nodes': `<strong>[NODE: MULTI-TENANT EKS/K3S COMPUTE POOL]</strong><br>
Nodes: 14 Nodes (m6i.2xlarge equivalent) · 112 vCPUs · 448 GiB RAM<br>
CNI & Mesh: Cilium eBPF packet routing + Istio Ambient Mesh<br>
Autoscaling: HPA target at 70% CPU/Memory with Cluster Autoscaler (Scale down delay: 300s)`,

    'gitops': `<strong>[NODE: ARGO-CD GITOPS CONTROL PLANE]</strong><br>
Sync State: Synced (Automated Self-Heal & Prune Enabled)<br>
Repositories: GitHub Monorepo / Helm Charts / SealedSecrets via HashiCorp Vault<br>
Deployment Frequency: Continuous Delivery with automated Blue/Green Canary Analysis`,

    'observability': `<strong>[NODE: TELEMETRY & OBSERVABILITY PIPELINE]</strong><br>
Metrics: VictoriaMetrics cluster collecting 2.5M metric samples/sec<br>
Tracing: Grafana Tempo distributed spans with OpenTelemetry Collector<br>
Logging: Grafana Loki multi-tenant log ingestion with retention policy of 30 days`,

    'storage': `<strong>[NODE: RESILIENT STORAGE LAYER]</strong><br>
Persistent Volumes: AWS EBS gp3 (CSI Driver) + Ceph Distributed Block Storage<br>
Backup: Velero daily snapshot schedules replicated cross-region to S3 glacier`
  };

  topoNodes.forEach(node => {
    node.addEventListener('click', () => {
      playClick(750, 0.03);
      topoNodes.forEach(n => n.classList.remove('active'));
      node.classList.add('active');
      const key = node.getAttribute('data-node');
      if (topoDetailBox && TOPOLOGY_DETAILS[key]) {
        topoDetailBox.innerHTML = TOPOLOGY_DETAILS[key];
      }
    });
  });

  /* ── 6. Interactive SRE Terminal Engine ── */
  const termScreen = document.getElementById('cockpit-term-screen');
  const termInput = document.getElementById('cockpit-term-input');
  const termChips = document.querySelectorAll('.chip-btn');

  const COCKPIT_COMMANDS = {
    help: `Available Cockpit Commands:
  - <span style="color:var(--c-cyan);">whoami</span>             : Engineer Bio & Credentials
  - <span style="color:var(--c-cyan);">kubectl get pods</span>   : Query cluster pod health
  - <span style="color:var(--c-cyan);">terraform plan</span>     : View cloud infrastructure state
  - <span style="color:var(--c-cyan);">pki audit</span>          : Validate TLS/SSL certificates
  - <span style="color:var(--c-cyan);">skills</span>             : Core technical competencies
  - <span style="color:var(--c-cyan);">finops</span>             : View cost optimization record
  - <span style="color:var(--c-cyan);">stats</span>              : Live compute metrics
  - <span style="color:var(--c-cyan);">clear</span>              : Flush terminal screen`,

    whoami: `<span style="color:#ffffff; font-weight:700;">Mohd Azam</span> — Senior SRE & Platform Engineer
Location: Hyderabad, India · 6+ Years Enterprise Cloud & Multi-Tenant SaaS
Specialties: Kubernetes, Terraform, Prometheus/Grafana Telemetry, Zero-Trust DevSecOps`,

    'kubectl get pods': `NAMESPACE      NAME                               READY   STATUS    RESTARTS   AGE
prod           haproxy-ingress-edge-7f89d-4k2l1   1/1     Running   0          48d
prod           traefik-gateway-69d9c7bb74-w8z9x   1/1     Running   0          48d
prod           codexrelic-api-78f99bd74b-k8q2m    1/1     Running   0          12d
prod           codexrelic-web-54cb7b9c9f-j2m4p    1/1     Running   0          12d
observability  victoriametrics-cluster-node-0     1/1     Running   0          94d
observability  tempo-distributed-ingester-0       1/1     Running   0          94d
observability  loki-distributed-gateway-7b98f     1/1     Running   0          94d
cert-manager   cert-manager-cainjector-8644       1/1     Running   0          120d`,

    'terraform plan': `Terraform v1.7.5 on linux_amd64
Initializing the backend... S3 State Lock: OK
Refreshing Terraform state in-memory prior to plan...
aws_eks_cluster.prod: Refreshing state... [id=k8s-prod-us-east-1]
aws_security_group.ingress: Refreshing state... [id=sg-0a84f]
aws_iam_role.sre_nodes: Refreshing state... [id=role-eks-nodes]

No changes. Your infrastructure matches the configuration.
0 to add, 0 to change, 0 to destroy.`,

    'pki audit': `[PKI HEALTH AUDIT]
Target: *.codexrelic.com & api.codexrelic.com
Issuer: Let's Encrypt (E1 Intermediate)
Key Type: ECDSA secp384r1 (High-grade cryptographic strength)
Expires In: 68 Days Remaining (Auto-renewal scheduled at T-30d via cert-manager)
Zero-Downtime Reloads: 100% SUCCESS · Ingress sync verified.`,

    skills: `TECHNICAL PROFICIENCIES:
• Orchestration: Kubernetes, Docker, Helm, ArgoCD, Cilium eBPF, Istio Ambient
• IaC & Cloud: Terraform, Terragrunt, AWS EKS/VPC, Azure DevOps, Oracle Cloud
• Observability: VictoriaMetrics, Prometheus, Grafana Tempo, Loki, New Relic, OpenTelemetry
• Languages & OS: Python, Go, Bash Shell, Linux (Ubuntu/RHEL/Debian), Windows Server`,

    finops: `FINOPS SAVINGS & IMPACT SUMMARY:
• Annual Recurring Savings: $4,300+/year achieved at Mitratech
• Redundant SQL Storage Blobs Eliminated: 1 TB cleaned ($1,500/yr saved)
• License & Asset Cleanup: $2,800/yr reclaimed
• Deployment Duration: Compressed from 50 minutes down to 10 minutes (80% toil reduction)`,

    stats: `Node Telemetry: ONLINE
Load Avg: 0.34, 0.45, 0.52 · Tasks: 142 active · Uptime: 48 days 14:22:10`
  };

  function runCommand(raw) {
    const cmd = (raw || '').trim().toLowerCase();
    if (!cmd) return;

    playClick(900, 0.02);

    if (cmd === 'clear') {
      if (termScreen) {
        termScreen.innerHTML = `
          <div><span class="term-prompt-txt">azam@codexrelic:~$</span> clear</div>
        `;
      }
      return;
    }

    // Add user command line
    const row = document.createElement('div');
    row.innerHTML = `<span class="term-prompt-txt">azam@codexrelic:~$</span> <span style="color:#ffffff;">${escapeHtml(raw)}</span>`;
    termScreen.appendChild(row);

    // Add response
    const resDiv = document.createElement('div');
    resDiv.style.color = '#cbd5e1';
    resDiv.style.whiteSpace = 'pre-wrap';
    resDiv.style.lineHeight = '1.55';
    resDiv.style.marginBottom = '6px';

    if (COCKPIT_COMMANDS[cmd]) {
      resDiv.innerHTML = COCKPIT_COMMANDS[cmd];
    } else {
      resDiv.innerHTML = `<span style="color:#f87171;">zsh: command not found: ${escapeHtml(raw)}</span>. Type <span style="color:var(--c-cyan);">'help'</span> for list of valid commands.`;
    }

    termScreen.appendChild(resDiv);
    termScreen.scrollTop = termScreen.scrollHeight;
  }

  if (termInput) {
    termInput.addEventListener('keydown', (e) => {
      if (e.key === 'Enter') {
        const v = termInput.value;
        termInput.value = '';
        runCommand(v);
      }
    });
  }

  termChips.forEach(chip => {
    chip.addEventListener('click', () => {
      const c = chip.getAttribute('data-cmd');
      if (termInput) termInput.value = c;
      runCommand(c);
    });
  });

  /* ── 7. Real-Time Telemetry WebSocket ── */
  const wsProto = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
  const wsHost = window.location.host || '127.0.0.1:8000';
  const wsUrl = `${wsProto}//${wsHost}/api/ws/stats`;

  function connectStats() {
    try {
      const ws = new WebSocket(wsUrl);
      const cpuCore0 = document.getElementById('gauge-cpu-core0');
      const cpuCore0Txt = document.getElementById('gauge-cpu-core0-txt');
      const cpuCore1 = document.getElementById('gauge-cpu-core1');
      const cpuCore1Txt = document.getElementById('gauge-cpu-core1-txt');
      const memFill = document.getElementById('gauge-mem-fill');
      const memTxt = document.getElementById('gauge-mem-txt');
      const swpFill = document.getElementById('gauge-swp-fill');
      const swpTxt = document.getElementById('gauge-swp-txt');
      const loadTxt = document.getElementById('val-load-avg');
      const uptimeTxt = document.getElementById('val-uptime');

      function formatBytes(bytes) {
        if (!bytes) return '0 B';
        const k = 1024;
        const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
      }

      ws.onmessage = (event) => {
        try {
          const stats = JSON.parse(event.data);
          if (stats.cpu && stats.cpu.length > 0) {
            if (cpuCore0 && cpuCore0Txt) {
              cpuCore0.style.width = `${stats.cpu[0]}%`;
              cpuCore0Txt.textContent = `${stats.cpu[0].toFixed(1)}%`;
            }
            if (stats.cpu.length > 1 && cpuCore1 && cpuCore1Txt) {
              cpuCore1.style.width = `${stats.cpu[1]}%`;
              cpuCore1Txt.textContent = `${stats.cpu[1].toFixed(1)}%`;
            }
          }
          if (stats.memory && memFill && memTxt) {
            memFill.style.width = `${stats.memory.percent}%`;
            memTxt.textContent = `${formatBytes(stats.memory.used)} / ${formatBytes(stats.memory.total)}`;
          }
          if (stats.swap && swpFill && swpTxt) {
            swpFill.style.width = `${stats.swap.percent}%`;
            swpTxt.textContent = `${formatBytes(stats.swap.used)} / ${formatBytes(stats.swap.total)}`;
          }
          if (stats.load && loadTxt) {
            loadTxt.textContent = `${stats.load[0].toFixed(2)}, ${stats.load[1].toFixed(2)}, ${stats.load[2].toFixed(2)}`;
          }
          if (stats.uptime && uptimeTxt) {
            uptimeTxt.textContent = stats.uptime;
          }
        } catch (e) {}
      };

      ws.onclose = () => {
        setTimeout(connectStats, 5000);
      };
    } catch (e) {}
  }
  connectStats();

  /* ── 8. Live CVE Intel Loader ── */
  const cveContainer = document.getElementById('cve-feed-container');
  if (cveContainer) {
    fetch('/api/cve-news')
      .then(res => res.json())
      .then(data => {
        if (data && data.length > 0) {
          cveContainer.innerHTML = data.slice(0, 4).map(item => `
            <a href="${item.link}" target="_blank" rel="noopener noreferrer" class="cve-item-box">
              <div class="cve-header-row">
                <span class="cve-id-tag">⚡ THREAT INTEL</span>
                <span style="font-family:var(--font-mono);font-size:0.68rem;color:var(--c-text-muted);">LIVE</span>
              </div>
              <div class="cve-title-txt">${escapeHtml(item.title)}</div>
            </a>
          `).join('');
        }
      })
      .catch(() => {});
  }

  /* ── 9. Command Palette ⌘K Modal ── */
  const cmdModal = document.getElementById('cockpit-cmd-modal');
  const cmdTrigger = document.getElementById('cmd-k-trigger');
  const cmdInput = document.getElementById('cockpit-cmd-search');
  const cmdList = document.getElementById('cockpit-cmd-results');
  const cmdClose = document.getElementById('cmd-close-btn');

  const COCKPIT_PAGES = [
    { title: 'Cockpit · Mission Control Matrix', subtitle: 'Live telemetry, topology map & interactive terminal', url: 'index.html', icon: '⚡' },
    { title: 'Production Architecture Projects', subtitle: 'Multi-tenant Kubernetes, SSL PKI & Observability', url: 'projects.html', icon: '🚀' },
    { title: 'Tech News Magazine', subtitle: 'Daily curated AI, kernel & cloud stories', url: 'tech-news.html', icon: '📰' },
    { title: 'DevSecOps & SRE Tools', subtitle: 'X.509 Certificate Decoder & MachineKey Generator', url: 'tools.html', icon: '🛠️' },
    { title: 'Cinema Logs & Vault', subtitle: 'Cinematography curation with SRE analogies', url: 'movies.html', icon: '🎬' },
    { title: 'Resume & Career Record', subtitle: '6+ years experience, FinOps impact & certifications', url: 'resume.html', icon: '📄' },
    { title: 'About Mohd Azam', subtitle: 'Career story from EA support to enterprise SRE', url: 'about.html', icon: '👤' },
    { title: 'Get in Touch', subtitle: 'Encrypted message gateway to private inbox', url: 'contact.html', icon: '✉️' }
  ];

  function openModal() {
    if (!cmdModal) return;
    playClick(750, 0.03);
    cmdModal.classList.add('active');
    if (cmdInput) {
      cmdInput.value = '';
      renderResults('');
      setTimeout(() => cmdInput.focus(), 40);
    }
  }

  function closeModal() {
    if (!cmdModal) return;
    cmdModal.classList.remove('active');
  }

  function renderResults(q) {
    if (!cmdList) return;
    const filter = (q || '').toLowerCase().trim();
    const matches = COCKPIT_PAGES.filter(p => 
      p.title.toLowerCase().includes(filter) || p.subtitle.toLowerCase().includes(filter)
    );

    if (matches.length === 0) {
      cmdList.innerHTML = `<div style="padding:16px;text-align:center;color:var(--c-text-muted);font-size:0.85rem;">No matching modules found</div>`;
      return;
    }

    cmdList.innerHTML = matches.map((item, idx) => `
      <div class="modal-result-item ${idx === 0 ? 'selected' : ''}" data-url="${item.url}">
        <div style="display:flex;align-items:center;gap:10px;">
          <span>${item.icon}</span>
          <div>
            <div style="font-weight:700;font-size:0.88rem;color:var(--c-text);">${item.title}</div>
            <div style="font-size:0.75rem;color:var(--c-text-secondary);">${item.subtitle}</div>
          </div>
        </div>
        <span style="font-family:var(--font-mono);font-size:0.72rem;color:var(--c-cyan);">Jump &rarr;</span>
      </div>
    `).join('');

    cmdList.querySelectorAll('.modal-result-item').forEach(el => {
      el.addEventListener('click', () => {
        closeModal();
        window.location.href = el.getAttribute('data-url');
      });
    });
  }

  if (cmdTrigger) cmdTrigger.addEventListener('click', openModal);
  if (cmdClose) cmdClose.addEventListener('click', closeModal);
  if (cmdModal) {
    cmdModal.addEventListener('click', (e) => {
      if (e.target === cmdModal) closeModal();
    });
  }

  if (cmdInput) {
    cmdInput.addEventListener('input', (e) => renderResults(e.target.value));
    cmdInput.addEventListener('keydown', (e) => {
      if (e.key === 'Escape') closeModal();
      if (e.key === 'Enter') {
        const sel = cmdList.querySelector('.modal-result-item.selected') || cmdList.querySelector('.modal-result-item');
        if (sel) sel.click();
      }
    });
  }

  window.addEventListener('keydown', (e) => {
    if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
      e.preventDefault();
      if (cmdModal && cmdModal.classList.contains('active')) closeModal();
      else openModal();
    } else if (e.key === 'Escape' && cmdModal && cmdModal.classList.contains('active')) {
      closeModal();
    }
  });

});

function escapeHtml(str) {
  return String(str).replace(/[&<>"']/g, (m) => ({
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
    '"': '&quot;',
    "'": '&#39;'
  }[m]));
}
