<div align="center">

# Free End-to-End DevOps Project

**Real-Time Implementation & SRE Portfolio Showcase**

*Built by Mohd Azam · 100% Free Tier Enterprise-Grade Infrastructure*

[![Azure DevOps](https://img.shields.io/badge/CI/CD-Azure%20DevOps-0078D4?logo=azure-devops)](https://dev.azure.com)
[![Kubernetes](https://img.shields.io/badge/Orchestration-K3s-326CE5?logo=kubernetes)](https://k3s.io)
[![MongoDB Atlas](https://img.shields.io/badge/Database-MongoDB%20Atlas-47A248?logo=mongodb)](https://mongodb.com/atlas)
[![Oracle Cloud](https://img.shields.io/badge/Hosting-Oracle%20Cloud%20Free-F80000?logo=oracle)](https://oracle.com/cloud/free)
[![GoDaddy](https://img.shields.io/badge/DNS-GoDaddy-00A4A6?logo=godaddy)](https://godaddy.com)
[![Let's Encrypt](https://img.shields.io/badge/SSL-Let's%20Encrypt-003A70?logo=letsencrypt)](https://letsencrypt.org/)
[![12-Factor](https://img.shields.io/badge/Architecture-12--Factor%20App-0078D4)](https://12factor.net/)

</div>

---

## 1. The Challenge (Or: Why I Built This)

`codexrelic.com` is a **100% free, end-to-end DevOps & SRE project** demonstrating real-time implementation of enterprise-grade infrastructure. 

Why free? Because I am broke and don't have money to spend on personal projects like any other student or professional. Just keeping it real! But honestly, building a production-grade, 12-Factor app on a $0 budget using the Oracle Cloud Always Free tier forces you to be creative.

Beyond the code, I'm a real human who loves tech as much as watching movies, history, and philosophy. Also, full disclosure: the code here was primarily written by AI, while I added the "human intelligence" as salt and pepper to make the curry—which is, theoretically, this project!

---

## 2. Infrastructure & GitOps (The Foundation)

**The Thought Process:** Working full-time means I don't have time to manually manage configurations. Necessity is the mother of invention! I needed a system that deploys itself while I'm busy.

**The Execution:**
- **GitOps via Argo CD:** Ensures the cluster state always matches Git. No manual `kubectl apply` drift.
- **K3s (Lightweight Kubernetes):** Perfect for our lightweight VM.
- **Oracle Cloud ARM VM:** Always Free (2 OCPU / 12 GB RAM). Shout out to Oracle for considering and thinking about people like us who need free compute!
- **GoDaddy DNS & Traefik:** Handles routing gracefully.
- **cert-manager:** Automated Let's Encrypt SSL provisioning so I don't have to remember to renew certs.

*War Story (Debugging ArgoCD):* When setting up ArgoCD behind Traefik, I hit an endless redirect loop because Argo expects HTTPS but Traefik proxies via HTTP. The fix? A sneaky `configMapGenerator` patch (`server.insecure="true"`) to disable Argo's internal TLS so it plays nicely with the ingress.

---

## 3. CI/CD & Cross-Compilation (The Delivery)

**The Thought Process:** The free Oracle VM is ARM64 (Ampere A1). Again, humor for cost: Ampere is the only free VM available! But Azure DevOps agents are standard x86. How do we build images without paying for expensive ARM runners?

**The Execution:**
- Leveraging **QEMU & Docker Buildx** in Azure DevOps pipelines to natively cross-compile `linux/arm64` images on `x86` agents.
- Pushing to DockerHub, and letting Argo CD handle the sync.
- Automated Checks for SSL expiry monitoring via a scheduled weekly cron pipeline.

---

## 4. Docker Hardening & Security (The Defense)

**The Thought Process:** Security conscious humor: I want to sleep good post-work. If this thing gets hacked and starts mining crypto, my $0 budget goes out the window!

**The Execution:** 
- **OWASP Compliant:** Secured against common web vulnerabilities via strict CSP headers, stateless JWTs, and cryptographic auth.
- **Docker Hardening:**
  - Multi-stage builds using `alpine:3.20` to reduce image bloat and attack surface.
  - Dropped root privileges immediately: running as a dedicated non-root `appuser`.
  - Minimal dependencies via virtual environments (`venv`).
  - Zero secrets in images or Git. **Azure Key Vault** (`kv-prod-codexrelic`, `kv-github-codexrelic`) handles all secrets dynamically.

*War Story (Annotation Limits):* When applying massive ArgoCD CRDs through the pipeline, Kubernetes rejected them with a `Too long: may not be more than 262144 bytes` annotation error. I had to bypass client-side limits entirely by forcing `kubectl apply --server-side`.

---

## 5. Authentication & Statelessness (The Application)

**The Thought Process:** I don't wish to maintain a lot of passwords. (Insert old person analogy: "Back in my day, we had one password, and it was written on a sticky note under the keyboard!"). 

**The Execution:** 
- **12-Factor App Compliant:** Fully stateless application design with externalized configuration.
- **Cryptographic 3-Factor Auth:** Uses Ed25519 WebCrypto + bcrypt + JWT for the admin panel.
- **Stateless JWTs:** Prevents session hijacking and keeps our MongoDB Atlas M0 Free cluster highly performant because there's absolutely no session lookup overhead.

---

## 6. Modern SEO & Observability (The Polish)

**The Thought Process:** SEO is just a buzzword, but for visibility (like in an organization, you need to voice out your opinion to be heard and recognized), you need it. If Google can't find it, does it even exist?

**The Execution:**
- **Modern SEO/SMO Architecture:** Canonical links, Open Graph, Twitter Cards, `robots.txt`, and XML Sitemaps injected across all public pages.
- **Observability:** OpenObserve (Logs & Metrics collection via Helm), tuned down to fit our tiny ARM VM without crashing it.

*War Story (Crashing the Database):* I initially tried deploying the full OpenObserve High-Availability Helm chart, and it crashed all pods because it expects a massive distributed database backend. The solution? Forcing `config.ZO_LOCAL_MODE="true"` to use a lightweight embedded database (sled/sqlite) which runs beautifully on the free tier.

---

## Live Environments

| Environment | URL | Purpose |
|-------------|-----|---------|
| Production | [codexrelic.com](https://codexrelic.com) | Live public site |
| Staging | [stage.codexrelic.com](https://stage.codexrelic.com) | Pre-prod smoke tests |
| UAT | [uat.codexrelic.com](https://uat.codexrelic.com) | Internal QA & acceptance |

---

## API Reference

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `GET` | `/api/movies` | Public | List movies with SRE analogies |
| `GET` | `/api/blogs` | Public | List blog posts |
| `POST` | `/api/login` | — | Authenticate (3-Factor DB Auth → JWT) |
| `POST` | `/api/admin/movies` | JWT | Add movie to CMS |
| `POST` | `/api/admin/blogs` | JWT | Add blog post to CMS |
| `POST` | `/api/admin/resume` | JWT | Upload LaTeX resume |
| `GET` | `/admin/dashboard.html` | JWT | Protected admin dashboard |

---

## Author
**Mohd Azam**
Site Reliability Engineer · DevOps · Platform Engineering
[codexrelic.com](https://codexrelic.com) · [LinkedIn](https://linkedin.com/in/mohdazam193)

---

## License
[Apache License 2.0](LICENSE)
