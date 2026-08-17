<div align="center">

# codexrelic.com

**Personal SRE & Platform Engineering Portfolio**

*Mohd Azam · Site Reliability Engineer · 6+ years in multi-tenant SaaS*

[![Azure DevOps](https://img.shields.io/badge/CI/CD-Azure%20DevOps-0078D4?logo=azure-devops)](https://dev.azure.com)
[![Docker](https://img.shields.io/badge/Containerised-Docker-2496ED?logo=docker)](https://docker.com)
[![MongoDB Atlas](https://img.shields.io/badge/Database-MongoDB%20Atlas-47A248?logo=mongodb)](https://mongodb.com/atlas)
[![Oracle Cloud](https://img.shields.io/badge/Hosting-Oracle%20Cloud%20Free-F80000?logo=oracle)](https://oracle.com/cloud/free)
[![Cloudflare](https://img.shields.io/badge/CDN-Cloudflare-F38020?logo=cloudflare)](https://cloudflare.com)
[![OWASP](https://img.shields.io/badge/Security-OWASP%20Top%2010%20Tested-brightgreen?logo=owasp)](https://owasp.org/www-project-top-ten/)
[![12-Factor](https://img.shields.io/badge/Architecture-12--Factor%20App-0078D4)](https://12factor.net/)

</div>

---

## Overview

`codexrelic.com` is a production-grade personal portfolio and blog built as a live SRE showcase.
Every infrastructure decision is intentional and documented — from zero-cost hosting to
cryptographic admin authentication — demonstrating the same practices applied in enterprise environments.

The site serves as both a public portfolio and a working proof of concept for:
- Multi-environment deployment pipelines (UAT → Stage → Prod)
- DevSecOps with container vulnerability scanning
- Cryptographic 3-factor authentication
- Infrastructure-as-code and automation-first operations

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
                        │   Cloudflare (Free Tier)        │
                        │   TLS · CDN · DDoS Protection   │
                        └────────────────┬────────────────┘
                                         │
                        ┌────────────────▼────────────────┐
                        │   Oracle Cloud ARM VM           │
                        │   Always Free · 2 OCPU · 12 GB │
                        │                                 │
                        │  Nginx (reverse proxy)          │
                        │  ├── uat.*      → :8001         │
                        │  ├── stage.*    → :8002         │
                        │  └── codexrelic.com → :8003     │
                        │                                 │
                        │  Docker Containers              │
                        │  ├── app-uat   (FastAPI)        │
                        │  ├── app-stage (FastAPI)        │
                        │  └── app-prod  (FastAPI)        │
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
  Azure DevOps    ───►  Azure Key Vault (per env)
  Pipeline              kv-uat-codexrelic
  (Build→Scan→Deploy)   kv-stage-codexrelic
                        kv-prod-codexrelic
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
| Containers | Docker + Docker Compose |
| Reverse Proxy | Nginx |
| CDN & TLS | Cloudflare Free |
| DNS | Cloudflare DNS |
| Database | MongoDB Atlas M0 Free |
| Secrets | Azure Key Vault (Standard, 3 vaults) |

### CI/CD & DevSecOps
| Layer | Technology |
|-------|-----------|
| Pipeline | Azure DevOps Pipelines |
| Container Registry | DockerHub |
| Vulnerability Scanning | Snyk (container scan, fail on HIGH) |
| IaC | Terraform (OCI provider) |
| Automation | Bash scripts (`automation/`) |

---

## Security Model

The admin interface uses **3-factor cryptographic authentication**:

```
Factor 1 → Username            (identity claim)
Factor 2 → Password            (bcrypt, cost 12)
Factor 3 → Ed25519 Private Key (asymmetric challenge-response)
```

### How it works
1. Browser fetches a fresh 32-byte random **challenge** from the server (`GET /api/auth/challenge`)
2. The challenge expires in **30 seconds** and is **one-time use** (replay-proof)
3. Browser signs `challenge:username` locally using the **Web Crypto API** — private key never leaves the device
4. Server verifies the **Ed25519 signature** against the stored public key
5. Server verifies the **bcrypt password** against the stored hash
6. On success, issues a **JWT cookie** (HS256, 24h expiry, `httponly` + `secure`)

### Why this is strong
| Attack Vector | Mitigation |
|---------------|-----------|
| Database dump | Public key + bcrypt hash — both useless without private key |
| Network interception | Private key never transmitted — only the signature |
| Brute force | Rate limited: 5 attempts/min per IP |
| Replay attack | 30-second challenge TTL + single use |
| Session forgery | HMAC-SHA256 JWT with 256-bit secret, per-environment |
| XSS session theft | `httponly` cookie — not accessible to JavaScript |

### Secrets management
All secrets are stored in **Azure Key Vault** — one vault per environment.
The pipeline reads secrets at deploy time and injects them as environment variables.
No secrets are stored in git, Docker images, or plain text files on the server.

---

## Infrastructure Cost

| Environment | Compute | Database | Total |
|-------------|---------|----------|-------|
| UAT | Oracle Cloud Free | Atlas M0 Free | **$0/month** |
| Stage | Oracle Cloud Free | Atlas M0 Free | **$0/month** |
| Prod | Oracle Cloud Free | Atlas M0 Free | **$0/month** |
| **Total** | | | **$0/month** |

> Sessions are stateless JWTs — no MongoDB session collection needed, so all environments
> remain on the Atlas M0 free tier indefinitely.

---

## Project Structure

```
codexrelic.com/
├── src/                          # Application source
│   ├── server.py                 # FastAPI application (413 lines)
│   ├── requirements.txt          # Python dependencies
│   ├── public/                   # Static site (HTML/CSS/JS)
│   │   ├── index.html            # Home — SRE portfolio
│   │   ├── blog.html             # Blog listing
│   │   ├── movies.html           # Movies + SRE analogies
│   │   ├── about.html
│   │   ├── resume.html
│   │   ├── contact.html
│   │   ├── community.html
│   │   ├── projects.html
│   │   ├── admin/
│   │   │   └── login.html        # Secure terminal-style login
│   │   └── assets/               # CSS, JS, images
│   └── templates/
│       └── admin/
│           └── dashboard.html    # Protected CMS dashboard
│
├── docker/                       # Container config
│   ├── Dockerfile                # Python 3.11-slim, Uvicorn on :8000
│   └── .dockerignore
│
├── ci-cd/                        # Pipeline definitions
│   └── docker/
│       └── azure-pipelines.yml   # Build → Snyk scan → Push → Deploy
│
├── iac/                          # Infrastructure as Code
│   └── terraform/                # OCI provider (Terraform)
│
├── automation/                   # Automation scripts
│   ├── README.md                 # Script index
│   ├── 01-auth-setup/
│   │   └── generate-keys.sh      # Ed25519 keypair + JWT secret generation
│   └── 02-keyvault/
│       └── create-and-populate-keyvaults.sh  # Azure KV provisioning
│
├── AUTH_SETUP.md                 # Local-only setup guide (gitignored)
├── LICENSE                       # Apache 2.0
└── README.md                     # This file
```

---

## CI/CD Pipeline

```
git push → main
    │
    ▼
┌─────────────────────────────────────────────────┐
│  Stage: BuildAndScan                            │
│  ├── Docker build (linux/arm64)                 │
│  ├── Snyk container vulnerability scan          │
│  │   └── Fails pipeline on HIGH severity CVEs  │
│  └── Push to DockerHub (tagged + latest)        │
└────────────────────┬────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────┐
│  Stage: DeployToUAT                             │
│  ├── Read secrets from kv-uat-codexrelic        │
│  ├── Render .env.uat                            │
│  └── SSH → OCI VM → docker compose up          │
└────────────────────┬────────────────────────────┘
                     │ (manual approval gate)
                     ▼
┌─────────────────────────────────────────────────┐
│  Stage: DeployToStage                           │
│  └── Same pattern → kv-stage-codexrelic         │
└────────────────────┬────────────────────────────┘
                     │ (manual approval gate)
                     ▼
┌─────────────────────────────────────────────────┐
│  Stage: DeployToProd                            │
│  └── Same pattern → kv-prod-codexrelic          │
└─────────────────────────────────────────────────┘
```

---

## API Reference

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `GET` | `/api/movies` | Public | List movies with SRE analogies |
| `GET` | `/api/blogs` | Public | List blog posts |
| `GET` | `/api/auth/challenge` | Public | Get Ed25519 login challenge |
| `POST` | `/api/login` | — | Authenticate (Ed25519 + bcrypt → JWT) |
| `POST` | `/api/admin/movies` | JWT | Add movie to CMS |
| `POST` | `/api/admin/blogs` | JWT | Add blog post to CMS |
| `POST` | `/api/admin/resume` | JWT | Upload LaTeX resume |
| `GET` | `/admin/dashboard.html` | JWT | Protected admin dashboard |

---

## Local Development

```bash
# Clone
git clone https://github.com/<your-username>/codexrelic.com.git
cd codexrelic.com

# Install dependencies
pip install -r src/requirements.txt

# Configure environment (copy and fill in values)
cp src/.env.example src/.env   # see AUTH_SETUP.md for key generation

# Run locally
cd src && uvicorn server:app --host 127.0.0.1 --port 8000 --reload
```

> **Note:** Admin login requires an Ed25519 private key. See `AUTH_SETUP.md`
> (local-only, gitignored) for key generation instructions.

---

## MongoDB Atlas Setup

This project uses a **single free MongoDB Atlas M0 cluster** to serve all three environments, maintaining data isolation through logical database names while keeping costs at $0/month.

1. Create an [MongoDB Atlas](https://www.mongodb.com/cloud/atlas) account and provision a **Shared M0 Free** cluster.
2. Under **Database Access**, create a user (e.g., `codexrelic_db_admin`) with a strong, auto-generated password.
3. Under **Network Access**, allow access from anywhere (`0.0.0.0/0`) or specifically your OCI VM's IP once provisioned.
4. Get your connection string from the **Connect** button (Python driver).
5. Format the connection string for each environment by injecting the password and appending the database name:
   - `mongodb+srv://user:pass@cluster.net/codexrelic_uat?retryWrites=true&w=majority`
   - `mongodb+srv://user:pass@cluster.net/codexrelic_stage?retryWrites=true&w=majority`
   - `mongodb+srv://user:pass@cluster.net/codexrelic_prod?retryWrites=true&w=majority`
6. Add these formatted strings to your Azure Key Vaults as the `MONGO-URI` secret.

---

## Azure DevOps Service Connection Setup

To allow the Azure DevOps pipeline to read secrets from Azure Key Vault, you must set up an **Azure Resource Manager** service connection.

1. Go to your Azure DevOps project → **Project Settings** (bottom left gear icon).
2. Under **Pipelines** → click **Service connections**.
3. Click **New service connection** → choose **Azure Resource Manager**.
4. Select **Service principal (automatic)** → click Next.
5. Choose your **Subscription** → set **Resource group** to your KV resource group (e.g., `rg-codexrelic`).
6. Name the connection `keyvalute-codex`.
7. Check **Grant access permission to all pipelines** → Save.

This automatically creates a service principal and assigns it Contributor access. You must then grant this service principal `Get` and `List` permissions on your Azure Key Vaults.

---

## Azure Key Vault Access Policy Setup

Before the pipeline or your user account can read/write secrets, you need to configure Access Policies in each Key Vault (`kv-uat-codexrelic`, `kv-stage-codexrelic`, `kv-prod-codexrelic`):

1. In the Azure Portal, open your Key Vault.
2. In the left sidebar, click **Access policies**.
3. Click **+ Create**.
4. Under **Secret permissions**, check the boxes for **Get** and **List**. (Check **Set** as well if you are doing this for your own user account to manually add secrets).
5. Click **Next** to go to the **Principal** tab.
6. Search for and select the principal:
   - To give the pipeline access, search for the service principal name associated with `keyvalute-codex`.
   - To give yourself access, search for your own Azure user account name/email.
7. Click **Next**, then **Next** again, and finally click **Create**.

---

## Manually Adding Secrets to Key Vault

If you prefer to add secrets manually via the Azure Portal instead of using the automation scripts, follow these steps for each of the three vaults (`kv-uat-codexrelic`, `kv-stage-codexrelic`, `kv-prod-codexrelic`):

1. In the Azure Portal, open your Key Vault.
2. In the left sidebar under **Objects**, click **Secrets**.
3. Click **+ Generate/Import**.
4. Set the **Upload options** to `Manual`.
5. Enter the **Name** and **Value** for each of the 5 required secrets:
   - `MONGO-URI`: Your MongoDB Atlas connection string (e.g., `mongodb+srv://.../codexrelic_uat`).
   - `ADMIN-USER`: The admin username (`azam`).
   - `ADMIN-PASS`: Your bcrypt-hashed password (or plaintext if the server hashes it - in this app it's the raw password, which the server compares). *Actually, the server expects the raw password and checks it against bcrypt if DB is connected, or falls back to env comparison. Enter your strong raw password here.*. Plain text password you would be using to login
   - `JWT-SECRET`: The 64-character hex string generated from `AUTH_SETUP.md`.
   - `ADMIN-ED25519-PUBLIC-KEY`: Your base64 public key generated from `AUTH_SETUP.md`.
6. Click **Create** for each secret.

---

## Automation

The `automation/` directory contains bash scripts that mirror every manual setup step.
Useful for repeating setups, onboarding new environments, or disaster recovery.

```bash
# Generate Ed25519 keypairs + JWT secrets for all 3 environments
bash automation/01-auth-setup/generate-keys.sh

# Create Azure Key Vaults and populate all secrets
bash automation/02-keyvault/create-and-populate-keyvaults.sh

# Format MongoDB connection strings and push directly to Key Vaults
bash automation/03-database/setup-mongo-strings.sh

# Bootstrap all Azure DevOps pipeline variables for Terraform IaC (one command)
bash automation/04-iac/bootstrap-pipeline-variables.sh
```

---

## Infrastructure as Code (IaC)

The infrastructure for this project is fully managed with **Terraform** and deployed via an **Azure DevOps** pipeline. All cloud resources run on **Oracle Cloud Infrastructure (OCI)** Always Free tier.

### Architecture

```
Azure DevOps Pipeline
  │
  ├── Stage 1: Terraform Plan   ──► OCI S3 State (Object Storage bucket)
  ├── Stage 2: Manual Approval  ──► You review & click Approve
  └── Stage 3: Terraform Apply  ──► Provisions OCI Ampere A1 VM
```

### Quick Start for New Contributors

If you have cloned this repo and want to spin up the infrastructure yourself, the entire pipeline variable setup is automated in a single command:

```bash
# Pre-requisites:
#   1. OCI CLI installed and configured (oci setup config)
#   2. Azure CLI installed and logged in (az login)
#   3. Azure DevOps extension: az extension add --name azure-devops

bash automation/04-iac/bootstrap-pipeline-variables.sh
```

This script will:
1. Read your `~/.oci/config` to extract all OCI identifiers
2. Generate a fresh **unencrypted** RSA key for Terraform (separate from your personal key)
3. Register the key in OCI Console automatically
4. Create the `codexrelic-tf-state` Object Storage bucket for Terraform state
5. Create/update the Azure DevOps `terraform` Variable Group with all 12 variables

Once it completes, trigger the pipeline in Azure DevOps. It will pause after `terraform plan` for your manual approval before applying anything.

> **Full variable reference:** See [`automation/04-iac/VARIABLE_REFERENCE.md`](automation/04-iac/VARIABLE_REFERENCE.md)

### Required Pipeline Variables (Summary)

All variables live in the Azure DevOps `terraform` Library Variable Group.

| Variable | Description | Secret |
|---|---|---|
| `TF_VAR_tenancy_ocid` | OCI Tenancy OCID | No |
| `TF_VAR_user_ocid` | OCI User OCID | No |
| `TF_VAR_fingerprint` | API signing key fingerprint | No |
| `TF_VAR_region` | OCI region (e.g. `ap-hyderabad-1`) | No |
| `TF_VAR_compartment_id` | Compartment OCID | No |
| `TF_VAR_availability_domain` | Availability domain | No |
| `TF_VAR_ssh_public_key` | SSH public key for VM access | No |
| `OCI_PRIVATE_KEY_B64` | Base64-encoded unencrypted RSA private key | **Yes** |
| `TF_STATE_BUCKET` | OCI Object Storage bucket name | No |
| `TF_STATE_ENDPOINT` | OCI S3-compatible endpoint URL | No |
| `TF_STATE_ACCESS_KEY` | OCI Customer Secret Key ID | No |
| `TF_STATE_SECRET_KEY` | OCI Customer Secret Key value | **Yes** |

### Key Design Decisions & Lessons Learned

> Full details in [`LEARNINGS_AND_ISSUES.md`](LEARNINGS_AND_ISSUES.md)

| # | Issue | Fix |
|---|---|---|
| 1 | Azure Service Principal cannot use `azurerm` backend via CLI auth | Migrated state storage to OCI Object Storage (S3-compatible) |
| 2 | `${TF_VAR_region}` evaluates empty in Azure DevOps bash | Use Azure DevOps macros `$(TF_VAR_region)` in `env:` block instead |
| 3 | OCI S3 SSL certificate mismatch | Added `force_path_style = true` to `backend "s3"` block |
| 4 | Terraform hangs silently for 50+ minutes | Always add `-input=false` to all Terraform commands in CI/CD |
| 5 | Variable Group vars not visible inside bash scripts | Must explicitly map every variable in the `env:` block of each step |
| 6 | Encrypted OCI API key fails in Terraform provider | Generate a dedicated **unencrypted** RSA key; store it **base64-encoded** as `OCI_PRIVATE_KEY_B64` |

---


## Author

**Mohd Azam**
Site Reliability Engineer · DevOps · Platform Engineering

[codexrelic.com](https://codexrelic.com) · [LinkedIn](https://linkedin.com/in/mohdazam193)

---

## License

[Apache License 2.0](LICENSE)
