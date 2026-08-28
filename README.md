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
<br>
[![GitOps](https://img.shields.io/badge/GitOps-Argo%20CD-EF7B4D?logo=argo)](https://argoproj.github.io/cd/)
[![OpenObserve](https://img.shields.io/badge/Observability-OpenObserve-FF4E00?logo=databricks)](https://openobserve.ai/)
[![Gemini](https://img.shields.io/badge/AI_Co--Pilot-Google%20Gemini-8E75B2?logo=google-gemini)](https://gemini.google.com/)
[![Antigravity](https://img.shields.io/badge/IDE-Antigravity-000000?logo=google)](https://github.com/google/antigravity)

</div>

---

## 1. The Challenge & The AI Co-Pilot

*Why free? Because I am broke and don't have money to burn on personal projects like other professionals. Just keeping it real! Beyond the code, I'm a real human who loves tech as much as watching movies, history, and philosophy.*

*Full disclosure: the code here was primarily written by my AI co-pilot, Gemini (via Antigravity). Working with Gemini was a wild ride. Sometimes it showcased sheer technical code-writing prowess, pinpointing complex troubleshooting issues with surgical precision. Other times... it hallucinated wildly and just unnecessarily added things to the recipe that I never asked for. But I loved every minute of it! I served as the 'human intelligence' salt and pepper to make this chaotic AI curry actually taste good and function in production.*

### The Technical Execution
`codexrelic.com` is a **100% free, end-to-end DevOps & SRE project** demonstrating real-time implementation of enterprise-grade infrastructure. 
Every architectural decision is intentional and documented. This repository serves as a blueprint for learning DevOps and building a production-ready application without spending a dime. It acts as a working proof of concept for:
- GitOps continuous deployment via Argo CD
- Kubernetes orchestration (K3s) with automated Let's Encrypt SSL provisioning
- ARM64 cross-compilation CI/CD pipelines
- Cryptographic 3-factor authentication (Ed25519 WebCrypto)
- Modern SEO/SMO architecture
- Infrastructure-as-code and Azure Key Vault secrets management
- **12-Factor App Compliant:** Fully stateless application design.
- **OWASP Compliant:** Secured against common web vulnerabilities via strict CSP headers, stateless JWTs, and cryptographic auth.

---

## 2. Architecture & Tech Stack

*A massive shoutout to the heroes of the free-tier world: Oracle Cloud, Argo CD, MongoDB, and OpenObserve. Without you, this project would just be a local Docker container melting my laptop. And regarding the Oracle VM: ARM processors are running everything today anyway, so deploying on Ampere isn't just taking free compute—it's me being 'visionary'.*

### The Technical Execution

```text
                        ┌─────────────────────────────────┐
                        │   GoDaddy                       │
                        │   DNS Management                │
                        └────────────────┬────────────────┘
                                         │
                        ┌────────────────▼────────────────┐
                        │   Oracle Cloud ARM VM           │
                        │   Always Free · 2 OCPU · 12 GB │
                        │                                 │
                        │   K3s Kubernetes Cluster        │
                        │                                 │
                        │   Traefik (Ingress Controller)  │
                        │   cert-manager (Let's Encrypt)  │
                        │                                 │
                        │   namespaces:                   │
                        │   ├── uat   (FastAPI Pod)       │
                        │   ├── stage (FastAPI Pod)       │
                        │   ├── prod  (FastAPI Pod + HPA) │
                        │   └── observability (OpenObserve)│
                        └────────────────┬────────────────┘
                                         │ pymongo SRV
                        ┌────────────────▼────────────────┐
                        │   MongoDB Atlas (Managed)       │
                        │   M0 Free Cluster               │
                        │   ├── codexrelic_uat            │
                        │   ├── codexrelic_stage          │
                        │   └── codexrelic_prod           │
                        └─────────────────────────────────┘

  CI/CD                 Secrets
  ──────                ───────
  Azure DevOps    ───►  Azure Key Vault
  Pipeline              (kv-prod-codexrelic)
  (Build→Scan→Deploy)   
```

### Application
| Layer | Technology |
|-------|-----------|
| Runtime | Python 3.11 |
| Framework | FastAPI + Uvicorn |
| Database | MongoDB Atlas (pymongo) |
| Auth | Ed25519 challenge-response + bcrypt + JWT |
| Frontend | Vanilla HTML/CSS/JS (no framework) |

### Infrastructure
| Layer | Technology |
|-------|-----------|
| Compute | Oracle Cloud Always Free ARM (Ampere A1) |
| Orchestration | K3s (Lightweight Kubernetes) + HPA Auto-Scaling |
| GitOps | Argo CD |
| Ingress & Routing | Traefik |
| SSL / TLS | cert-manager + Let's Encrypt |
| Observability | OpenObserve (Logs & Metrics collection via Helm) |
| DNS | GoDaddy |
| Database | MongoDB Atlas M0 Free |
| Secrets | Azure Key Vault (`kv-prod-codexrelic`, `kv-github-codexrelic`) |

### CI/CD & DevSecOps
| Layer | Technology |
|-------|-----------|
| Pipeline | Azure DevOps Pipelines |
| Container Build | Docker + QEMU (Cross-compiling linux/arm64 on x86 agents) |
| Container Registry | DockerHub |
| IaC | Terraform (OCI provider) |
| Automated Checks | Scheduled pipelines for SSL expiry monitoring |

---

## 3. Infrastructure & GitOps

*Working full-time means I don't have the energy to manually run `kubectl apply` at 2 AM while half-asleep. Necessity is the mother of invention! A glorious shoutout to GitOps—thank you for making it possible to push code, go to bed, and let the machines do the heavy lifting while I dream.*

### The Technical Execution
- **GitOps via Argo CD:** Ensures the cluster state always matches Git. No manual `kubectl apply` drift.
- **K3s (Lightweight Kubernetes):** Perfect for our lightweight VM.
- **cert-manager:** Automated Let's Encrypt SSL provisioning so I don't have to remember to renew certs.

*War Story (Debugging ArgoCD):* When setting up ArgoCD behind Traefik, I hit an endless redirect loop because Argo expects HTTPS but Traefik proxies via HTTP. The fix? A sneaky `configMapGenerator` patch (`server.insecure="true"`) to disable Argo's internal TLS so it plays nicely with the ingress.

---

## 4. Docker Hardening & Security

*Security conscious humor: I want to sleep good post-work. If this gets hacked and starts mining crypto, my glorious $0 budget goes out the window!*

### The Technical Execution
- **Docker Hardening:**
  - Multi-stage builds using `alpine:3.20` to reduce image bloat and attack surface.
  - Dropped root privileges immediately: running as a dedicated non-root `appuser`.
  - Minimal dependencies via virtual environments (`venv`).
  - Zero secrets in images or Git. **Azure Key Vault** handles all secrets dynamically.

*War Story (Annotation Limits):* When applying massive ArgoCD CRDs through the pipeline, Kubernetes rejected them with a `Too long: may not be more than 262144 bytes` annotation error. I had to bypass client-side limits entirely by forcing `kubectl apply --server-side`.

---

## 5. Authentication & Statelessness

*I refuse to maintain a massive database of passwords. Back in my day, we had one password, and it was written on a sticky note under the keyboard! Now we use Ed25519 WebCrypto.*

### The Technical Execution
- **12-Factor App Compliant:** Fully stateless application design with externalized configuration.
- **Cryptographic 3-Factor Auth:** Uses Ed25519 WebCrypto + bcrypt + JWT for the admin panel.
- **Stateless JWTs:** Prevents session hijacking and keeps our MongoDB Atlas M0 Free cluster highly performant because there's absolutely no session lookup overhead.

---

## 6. Modern SEO & Observability

*SEO is a buzzword, but much like working in a large corporate organization—if you don't voice your opinion loudly in meetings, you don't exist. If Google doesn't see my site, does it even exist? I had to yell at the search engine so I could be recognized.*

### The Technical Execution
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
