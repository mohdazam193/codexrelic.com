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

## Overview

`codexrelic.com` is a **100% free, end-to-end DevOps & SRE project** demonstrating real-time implementation of enterprise-grade infrastructure. 
Every architectural decision is intentional and documented — from zero-cost cloud hosting to continuous GitOps deployments and cryptographic admin authentication. 

This repository serves as a blueprint for learning DevOps and building a production-ready application without spending a dime. It acts as a working proof of concept for:
- GitOps continuous deployment via Argo CD
- Kubernetes orchestration (K3s) with automated Let's Encrypt SSL provisioning
- ARM64 cross-compilation CI/CD pipelines
- Cryptographic 3-factor authentication (Ed25519 WebCrypto)
- Modern SEO/SMO architecture (Canonical, Open Graph, Twitter Cards, Sitemaps)
- Infrastructure-as-code and Azure Key Vault secrets management
- **12-Factor App Compliant:** Fully stateless application design with externalized configuration and dependencies.
- **OWASP Compliant:** Secured against common web vulnerabilities via strict CSP headers, stateless JWTs, and cryptographic auth.

---

## Live Environments

| Environment | URL | Purpose |
|-------------|-----|---------|
| Production | [codexrelic.com](https://codexrelic.com) | Live public site |
| Staging | [stage.codexrelic.com](https://stage.codexrelic.com) | Pre-prod smoke tests |
| UAT | [uat.codexrelic.com](https://uat.codexrelic.com) | Internal QA & acceptance |

---

## Architecture

```
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
  Azure DevOps    ───►  Azure DevOps Library
  Pipeline              Variable Groups (per env)
  (Build→Scan→Deploy)   - uat-variables
                        - stage-variables
                        - prod-variables
```

---

## Tech Stack

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

## Security Considerations in the Modern World

In a modern threat landscape, relying on network perimeters is insufficient. This project adopts a **Zero Trust** mindset and modern security practices:

- **Stateless Authentication:** Prevents session hijacking and eliminates the need for shared session stores.
- **Secrets Management:** No secrets are stored in Git or environment variables. Azure Key Vault serves as the central source of truth.
- **Minimal Attack Surface:** Only ports 80/443 are exposed. Traefik acts as the single entry point, terminating TLS.

The admin interface itself uses **3-factor database-backed authentication**:

```
Factor 1 → Username
Factor 2 → Password (bcrypt, cost 12)
Factor 3 → Unique Private Key per user (bcrypt, cost 12)
```

### How it works
1. **Generate Credentials:** The user creates an admin JSON payload locally by running `python3 automation/01-auth-setup/generate_admin_json.py` in their terminal.
2. **Add to Database:** The user adds this payload to their database:
   - Open MongoDB Compass and connect to the Atlas cluster.
   - Expand the specific environment database (e.g., `codexrelic_uat` or `codexrelic_prod`).
   - Click the **`+`** icon to create a new collection and name it precisely **`admin_users`**.
   - Open the new `admin_users` collection, click **ADD DATA** → **Insert Document**.
   - Switch to the `{}` (JSON) view and paste the generated JSON payload.
3. **Login:** The browser submits the `username`, `password`, and `private_key` directly to the `/api/login` endpoint over HTTPS.
4. **Verification:** The server looks up the user in MongoDB and verifies both the password and the private key using `bcrypt`.
5. **Success:** On success, the server issues a **stateless JWT cookie** (HS256, 24h expiry, `httponly` + `secure`).

### Secrets management
Secrets are managed externally in **Azure Key Vault**. 
The setup pipelines dynamically fetch secrets from the vaults (`kv-prod-codexrelic`, `kv-github-codexrelic`) and inject them securely into the Kubernetes cluster. No secrets are stored in git, Azure DevOps variables, Docker images, or plain text files on the server.

---

## Infrastructure Cost

| Environment | Compute | Database | Total |
|-------------|---------|----------|-------|
| UAT | Oracle Cloud Free | Atlas M0 Free | **$0/month** |
| Stage | Oracle Cloud Free | Atlas M0 Free | **$0/month** |
| Prod | Oracle Cloud Free | Atlas M0 Free | **$0/month** |
| **Total** | | | **$0/month** |

> **Note:** The entire infrastructure is 100% free. The *only* potential cost is purchasing a custom domain name (via GoDaddy or any registrar) if you want a custom URL.
> Sessions are stateless JWTs — no MongoDB session collection needed, so all environments
> remain on the Atlas M0 free tier indefinitely.

---

## Project Structure

```
codexrelic.com/
├── src/                          # Application source
│   ├── server.py                 # FastAPI application
│   ├── requirements.txt          # Python dependencies
│   ├── public/                   # Static site (HTML/CSS/JS)
│   └── templates/                # Protected CMS dashboard
│
├── ci-cd/                        # Pipeline definitions
│   ├── argo/                     # Argo CD manifests and kustomizations
│   ├── infrastructure/
│   │   └── azure-pipelines-argocd-setup.yml # ArgoCD setup and secrets injection pipeline
│   └── docker/
│       ├── azure-pipelines-build.yml     # QEMU setup, Docker build (ARM64), publish manifests
│       ├── azure-pipelines-release.yml   # Application release triggers (if applicable)
│       └── azure-pipelines-ssl-check.yml # Scheduled cron pipeline for SSL verification
│
├── kubernetes/                   # Kubernetes manifest templates
│   ├── deployment.yaml           # App Deployment (FastAPI)
│   ├── service.yaml              # ClusterIP Service
│   ├── ingress.yaml              # Traefik Ingress with Let's Encrypt TLS annotations
│   └── clusterissuer.yaml        # cert-manager ACME configuration
│
├── docker/                       # Container config
│   └── Dockerfile                # Python 3.11-slim, Uvicorn on :8000
│
├── iac/                          # Infrastructure as Code
│   └── terraform/                # OCI provider (Terraform)
│
├── automation/                   # Automation scripts
│   ├── README.md                 # Script index
│   └── ...
│
├── docs/                         # Additional documentation
│   └── LEARNINGS_AND_ISSUES.md   # Architectural decisions, bugs, and pipeline learnings
├── AUTH_SETUP.md                 # Local-only setup guide (gitignored)
├── LICENSE                       # Apache 2.0
└── README.md                     # This file
```

---

## CI/CD Pipeline Architecture & GitOps

The deployment pipeline is split into build and continuous deployment (GitOps) phases, accommodating cross-architecture compilation and automated syncing via Argo CD:

```
git push → main
    │
    ▼
┌──────────────────────────────────────────────────────────┐
│  Stage: Build (azure-pipelines-build.yml)                │
│  ├── Register QEMU binfmt for ARM64 cross-compilation    │
│  ├── Docker buildx build --platform linux/arm64          │
│  ├── Push to DockerHub (tagged + latest)                 │
│  └── Update Kubernetes manifests / triggers              │
└────────────────────────┬─────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────┐
│  GitOps: Continuous Deployment (Argo CD)                 │
│  ├── Argo CD detects changes in the Git repository       │
│  ├── Automatically syncs cluster state with Git          │
│  ├── Deploys to `uat`, `stage`, and `prod` namespaces    │
│  └── Applies ConfigMaps, Secrets, and Deployments        │
└──────────────────────────────────────────────────────────┘

*Note: Core infrastructure like Argo CD itself and OpenObserve are deployed via dedicated setup pipelines (`azure-pipelines-argocd-setup.yml`) that fetch secrets directly from Azure Key Vault and deploy over SSH via server-side apply.*
```

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
