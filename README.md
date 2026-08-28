<div align="center">

<img src="./codexrelic-logo.svg" alt="CodexRelic" width="420">

# Free End-to-End DevOps Project

### A real production-style SRE playground — built on a $0 budget.

<p>
  <a href="https://codexrelic.com"><strong>🌐 Live Site</strong></a>
  ·
  <a href="https://stage.codexrelic.com">Staging</a>
  ·
  <a href="https://uat.codexrelic.com">UAT</a>
</p>

<p>
  <img src="https://img.shields.io/badge/CI%2FCD-Azure%20DevOps-0078D4?logo=azure-devops" alt="Azure DevOps">
  <img src="https://img.shields.io/badge/Kubernetes-K3s-326CE5?logo=kubernetes" alt="K3s">
  <img src="https://img.shields.io/badge/GitOps-Argo%20CD-EF7B4D?logo=argo" alt="Argo CD">
  <img src="https://img.shields.io/badge/Observability-OpenObserve-FF4E00" alt="OpenObserve">
  <img src="https://img.shields.io/badge/Database-MongoDB%20Atlas-47A248?logo=mongodb" alt="MongoDB Atlas">
  <img src="https://img.shields.io/badge/Cloud-Oracle%20Always%20Free-F80000?logo=oracle" alt="Oracle Cloud">
</p>

<p>
  <img src="https://img.shields.io/badge/Runtime-Python%203.11-3776AB?logo=python" alt="Python">
  <img src="https://img.shields.io/badge/Framework-FastAPI-009688?logo=fastapi" alt="FastAPI">
  <img src="https://img.shields.io/badge/IaC-Terraform-844FBA?logo=terraform" alt="Terraform">
  <img src="https://img.shields.io/badge/Security-OWASP%20%7C%20Ed25519%20%7C%20JWT-black" alt="Security">
</p>

</div>

---

## ⚡ What is CodexRelic?

**CodexRelic is my end-to-end DevOps & SRE portfolio project.**

The goal is simple:

> **Build something that looks and behaves like a real production platform — without paying for a personal cloud lab.**

Why free?

**Because I am broke and don't have money to burn on personal projects like other professionals. Just keeping it real!** 😄

Beyond the code, I'm a real human who loves tech as much as watching movies, history, and philosophy.

Everything is intentionally wired together: infrastructure, Kubernetes, CI/CD, GitOps, secrets, security, observability, DNS, TLS, databases, environments and application delivery.

It is not a collection of disconnected demos.

**It is one living system.**

---

## 🧭 The Stack at a Glance

| Layer | Technology |
|---|---|
| ☁️ Compute | Oracle Cloud Always Free — Ampere ARM |
| ☸️ Kubernetes | K3s + HPA |
| 🚦 Ingress | Traefik |
| 🔐 TLS | cert-manager + Let's Encrypt |
| 🔄 GitOps | Argo CD |
| 🚀 CI/CD | Azure DevOps Pipelines |
| 🐳 Containers | Docker + QEMU |
| 📦 Registry | DockerHub |
| 🗄️ Database | MongoDB Atlas M0 |
| 🔑 Secrets | Azure Key Vault |
| 📊 Observability | OpenObserve |
| 🌍 DNS | GoDaddy |
| 🏗️ IaC | Terraform |
| 🐍 Backend | Python 3.11 + FastAPI + Uvicorn |
| 🔒 Auth | Ed25519 + bcrypt + JWT |
| 🎨 Frontend | Vanilla HTML / CSS / JavaScript |

---

## 🏗️ End-to-End Architecture

One `git push` kicks off the complete delivery chain: the code is sent to **Azure DevOps and the private GitHub repository**, Azure Pipelines handles **CI/CD + Infrastructure as Code**, DockerHub stores the ARM64 image, Terraform provisions the Oracle Cloud infrastructure, and Argo CD reconciles the Kubernetes application state.

<p align="center">
  <img src="./codexrelic-architecture-animated.gif" alt="Animated CodexRelic end-to-end DevOps and SRE architecture diagram" width="100%">
</p>

> **This is the actual platform flow — not a generic DevOps reference architecture.**

## 🏗️ Architecture

```text
                         ┌──────────────────────┐
                         │       GoDaddy        │
                         │     DNS Management   │
                         └──────────┬───────────┘
                                    │
                                    ▼
                  ┌────────────────────────────────┐
                  │      Oracle Cloud ARM VM        │
                  │       Always Free Tier          │
                  │         2 OCPU · 12 GB          │
                  │                                │
                  │              K3s               │
                  │        Kubernetes Cluster      │
                  │                                │
                  │   ┌─────────────────────────┐  │
                  │   │        Traefik          │  │
                  │   │      Ingress/TLS        │  │
                  │   └────────────┬────────────┘  │
                  │                │               │
                  │    ┌───────────┼───────────┐   │
                  │    │           │           │   │
                  │   UAT        STAGE        PROD  │
                  │    │           │           │   │
                  │ FastAPI      FastAPI     FastAPI│
                  │                          + HPA  │
                  │                                │
                  │        Observability            │
                  │          OpenObserve             │
                  └───────────────┬────────────────┘
                                  │
                                  │ pymongo SRV
                                  ▼
                       ┌──────────────────────┐
                       │    MongoDB Atlas     │
                       │      M0 Free         │
                       │                      │
                       │  UAT · STAGE · PROD  │
                       └──────────────────────┘


        ┌───────────────────┐
        │   Azure DevOps    │
        │ Build → Scan →    │
        │ Deploy            │
        └─────────┬─────────┘
                  │
                  ▼
        ┌───────────────────┐
        │   Azure Key Vault │
        │      Secrets      │
        └───────────────────┘
```

---

## 🚀 What This Project Demonstrates

### 🔄 GitOps Delivery

**Argo CD** continuously reconciles the Kubernetes application state with Git.

Azure Pipelines is responsible for the CI/CD workflow and infrastructure deployment. Argo CD then keeps the Kubernetes application state aligned with the declared configuration.

Because I work full-time, I don't have the energy to manually run:

```bash
kubectl apply
```

at 2 AM while half-asleep.

**Necessity is the mother of invention!**

Push code, go to bed, and let the machines do the heavy lifting while I dream. 😴

**Git is the source of truth. Azure Pipelines moves the change through the delivery process; Argo CD keeps Kubernetes reconciled.**

---

### ☸️ Lightweight Kubernetes

The platform runs on **K3s**, deliberately chosen for a small ARM VM.

It provides:

- Kubernetes orchestration
- Environment isolation
- Production-style ingress
- Horizontal Pod Autoscaling in production
- Automated TLS
- Resource-efficient operation

---

### 🔐 Security by Design

I want to sleep good after work. If this gets hacked and starts mining crypto, my glorious **$0 budget** goes out the window. 😂

The project deliberately avoids putting secrets into source control or container images.

Security includes:

- Ed25519 WebCrypto challenge-response authentication
- bcrypt password protection
- Stateless JWT authentication
- Non-root containers
- Strict Content Security Policy headers
- Externalized secrets through Azure Key Vault
- Minimal Alpine-based container images

---

### 🐳 Container Hardening

The Docker images use:

- Multi-stage builds
- `alpine:3.20`
- Dedicated non-root `appuser`
- Python virtual environments
- Minimal runtime dependencies
- No embedded secrets

The objective is simple:

**Keep the image small. Keep the attack surface smaller.**

### 💥 OpenObserve Was Too Heavy

I initially tried deploying the full OpenObserve High-Availability Helm chart.

It crashed all the pods because it expected a much larger distributed database backend.

The solution?

Force:

```text
ZO_LOCAL_MODE=true
```

and use a lightweight embedded database.

**Sometimes the best scaling strategy is simply not deploying the thing you don't need.**

---

## 🧪 Three Environments

| Environment | URL | Purpose |
|---|---|---|
| 🟢 **Production** | [codexrelic.com](https://codexrelic.com) | Live public site |
| 🟡 **Staging** | [stage.codexrelic.com](https://stage.codexrelic.com) | Pre-production smoke testing |
| 🔵 **UAT** | [uat.codexrelic.com](https://uat.codexrelic.com) | QA & acceptance testing |

Each environment has its own Kubernetes namespace and MongoDB database.

---

## 📊 Observability

SEO is a buzzword, but much like working in a large corporate organization — if you don't voice your opinion loudly in meetings, you don't exist.

If Google doesn't see my site, **does it even exist?** 😂

I had to yell at the search engine so I could be recognized.

### Observability

**OpenObserve** handles log and metric collection through Helm.

The important part is not simply installing an observability platform.

It is making one fit.

The original high-availability deployment was too heavy for the free ARM VM. The solution was to run OpenObserve in lightweight local mode using:

```text
ZO_LOCAL_MODE=true
```

Result:

**Useful observability without turning a free-tier VM into a space heater.**

---

## 🧠 The Engineering War Stories

This repository also documents the things that **went wrong**.

Because that's where the interesting engineering happens.

Production engineering isn't just about showing the architecture diagram when everything works.

It's also about the moment when Kubernetes tells you:

> **"No."**

and you figure out why.

### 💥 Argo CD + Traefik Redirect Loop

Argo CD behind Traefik initially produced an endless HTTPS redirect.

The issue:

```text
Client
  ↓ HTTPS
Traefik
  ↓ HTTP
Argo CD
  ↓
"Why aren't you HTTPS?"
```

The fix was configuring:

```text
server.insecure=true
```

through the deployment configuration so TLS termination could remain at the ingress layer.

---

### 📦 Kubernetes Annotation Limit

Large Argo CD CRDs hit Kubernetes' annotation size limit:

```text
Too long: may not be more than 262144 bytes
```

The deployment was changed to use:

```bash
kubectl apply --server-side
```

Sometimes production engineering is just finding the one flag that nobody told you about.

---

### 📊 OpenObserve Was Too Heavy

The initial HA Helm deployment overwhelmed the tiny free-tier environment.

Instead of throwing more hardware at it:

**the architecture was simplified.**

That is one of the central ideas behind this project:

> **Good engineering is not always about adding more infrastructure. Sometimes it is about removing it.**

---

## 🔐 Authentication Architecture

I refuse to maintain a massive database of passwords.

Back in my day, we had one password, and it was written on a sticky note under the keyboard. 😄

Now we use Ed25519 WebCrypto.

The admin authentication flow combines:

```text
Ed25519 WebCrypto
        +
bcrypt
        +
JWT
        ↓
Stateless Authentication
```

The application follows a **12-Factor style architecture**, keeping configuration externalized and application state out of the containers.

---

## 🌐 API

| Method | Endpoint | Auth | Purpose |
|---|---|---|---|
| `GET` | `/api/movies` | Public | List movies with SRE analogies |
| `GET` | `/api/blogs` | Public | List blog posts |
| `POST` | `/api/login` | — | Authenticate and issue JWT |
| `POST` | `/api/admin/movies` | JWT | Add movie |
| `POST` | `/api/admin/blogs` | JWT | Add blog post |
| `POST` | `/api/admin/resume` | JWT | Upload LaTeX resume |
| `GET` | `/admin/dashboard.html` | JWT | Protected admin dashboard |

---

## 🛡️ DevSecOps Pipeline

```text
                    Git Push
                       │
                       ▼
              ┌─────────────────┐
              │  Azure DevOps   │
              └────────┬────────┘
                       │
              ┌────────▼────────┐
              │      Build      │
              └────────┬────────┘
                       │
              ┌────────▼────────┐
              │   Security Scan │
              └────────┬────────┘
                       │
              ┌────────▼────────┐
              │ Docker + QEMU   │
              │   linux/arm64   │
              └────────┬────────┘
                       │
                       ▼
                  DockerHub
                       │
                       ▼
                   Argo CD
                       │
                       ▼
                 K3s Cluster
```

The pipeline also includes scheduled SSL-expiry monitoring.

---

## 💰 The $0 Infrastructure Challenge

The project deliberately uses free tiers wherever practical.

A massive shoutout to the heroes of the free-tier world: **Oracle Cloud, Argo CD, MongoDB and OpenObserve.**

Without you, this project would just be a local Docker container melting my laptop. 😂

And regarding the Oracle ARM VM:

> ARM processors are running everything today anyway, so deploying on Ampere isn't just taking free compute — **it's me being "visionary."** 😎

Here's the stack:

```text
Oracle Cloud        → Compute
MongoDB Atlas       → Database
Let's Encrypt       → TLS
Argo CD             → GitOps
K3s                 → Kubernetes
OpenObserve         → Observability
Azure DevOps        → CI/CD
Azure Key Vault     → Secrets
```

The point isn't that enterprise infrastructure should always cost $0.

The point is:

> **You don't need a huge cloud bill to learn how enterprise infrastructure actually works.**

---

## 🤖 The AI Co-Pilot

Full disclosure:

A significant portion of the code was written with **Gemini via Antigravity**.

It was an interesting collaboration.

Sometimes the AI produced technically excellent solutions and diagnosed problems with impressive precision.

Other times it confidently invented complexity that nobody ordered.

My role was essentially:

```text
AI
 ↓
Generate
 ↓
Break something
 ↓
Human investigates
 ↓
Question assumptions
 ↓
Simplify
 ↓
Deploy
 ↓
Repeat
```

The important lesson wasn't **"AI wrote the code."**

It was learning how to **review, challenge, troubleshoot and productionize AI-generated code.**

---

## 🎯 Why I Built This

I wanted a project that demonstrates more than:

> "I know Docker."

Or:

> "I have worked with Kubernetes."

Instead, I wanted something where the pieces actually interact:

**Infrastructure → Application → CI/CD → GitOps → Kubernetes → Security → Secrets → Observability → Production**

This repository is my attempt to build that system from scratch.

And yes — I built it because I like this stuff.

I also don't have an enterprise cloud budget sitting around for personal experiments.

So I made the constraint part of the engineering challenge.

---

## 👨‍💻 About Me

### **Mohd Azam**

**Site Reliability Engineer · DevOps · Platform Engineering**

I enjoy experimenting with infrastructure, breaking things, figuring out why they broke, and then automating the fix.

If you're interested in DevOps, SRE, cloud infrastructure, Kubernetes or the engineering behind this project:

🌐 **[codexrelic.com](https://codexrelic.com)**  
💼 **[LinkedIn](https://linkedin.com/in/mohdazam193)**

---

<div align="center">

### Built with curiosity.  
### Debugged with persistence.  
### Deployed for $0.

**⭐ If you find this useful, consider giving the repository a star.**

</div>

---

## 📜 License

[Apache License 2.0](LICENSE)
