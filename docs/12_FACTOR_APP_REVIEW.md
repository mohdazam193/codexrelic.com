# 12-Factor App Methodology Review
**Application:** codexrelic.com Full Stack (`server.py`, `public/`, `templates/`, `automation/`)
**Date:** August 2026

This document reviews the `codexrelic.com` application against the industry-standard **12-Factor App** methodology for building robust, scalable, and cloud-native software-as-a-service (SaaS) applications.

---

### 1. Codebase 🟢 (Pass)
*One codebase tracked in revision control, many deploys.*
- **Implementation:** The entire application (backend `server.py`, frontend `public/` assets, secure `templates/`, Dockerfiles, Terraform IaC, and CI/CD pipelines) is tracked in a single Git repository hosted on GitHub/Azure DevOps.
- **Deploys:** This exact same codebase is deployed across three distinct environments (UAT, Stage, and Production).

### 2. Dependencies 🟢 (Pass)
*Explicitly declare and isolate dependencies.*
- **Implementation:** Python backend dependencies are explicitly pinned in `src/requirements.txt`. The frontend (`public/`) is built with Vanilla HTML/JS/CSS, deliberately having zero NPM/Node dependencies to reduce supply chain risk. The entire application is containerized using Docker, ensuring absolute isolation of the runtime environment (Python 3.11-slim) regardless of the host OS.

### 3. Config 🟢 (Pass)
*Store config in the environment.*
- **Implementation:** Zero credentials or environment-specific configurations are hardcoded. Everything (`MONGO_URI`, `JWT_SECRET`, `ADMIN_PASS`, etc.) is loaded via environment variables using `os.getenv()`.
- **Secrets Management:** Environment variables are securely injected at deployment time by reading directly from environment-specific Azure Key Vaults.

### 4. Backing Services 🟢 (Pass)
*Treat backing services as attached resources.*
- **Implementation:** MongoDB Atlas is treated strictly as an attached resource. The application connects via a standard connection string URI. If the database needs to be migrated or scaled, only the `MONGO_URI` environment variable changes — no code changes are required.

### 5. Build, Release, Run 🟢 (Pass)
*Strictly separate build and run stages.*
- **Implementation:** The Azure DevOps pipeline strictly enforces this:
  - **Build:** The Docker image is built and scanned by Snyk, then pushed to DockerHub with a unique immutable tag (`BuildId`).
  - **Release:** The deployment stages (UAT/Stage/Prod) combine the immutable Docker image with the environment-specific Key Vault secrets (creating a `.env` file).
  - **Run:** The OCI VM pulls the image and runs it with the release configuration via `docker compose`.

### 6. Processes 🟢 (Pass)
*Execute the app as one or more stateless processes.*
- **Implementation:** The FastAPI application is entirely stateless. 
- **State isolation:** By moving to Ed25519 cryptographic challenge-response and signed JWT cookies, the application requires absolutely no "sticky sessions" or server-side memory state for authentication. Any container instance can handle any request.

### 7. Port Binding 🟢 (Pass)
*Export services via port binding.*
- **Implementation:** The application is self-contained. The ASGI server Uvicorn binds to port `8000` (`uvicorn server:app --port 8000`), serving both the FastAPI backend and the static frontend assets (`public/`). Nginx acts purely as a reverse proxy to route external traffic to this bound port.

### 8. Concurrency 🟢 (Pass)
*Scale out via the process model.*
- **Implementation:** Because the app is completely stateless (Factor 6), concurrency can be achieved horizontally by simply spinning up more Docker containers behind Nginx, or vertically by adding Uvicorn worker processes (`--workers`).

### 9. Disposability 🟢 (Pass)
*Maximize robustness with fast startup and graceful shutdown.*
- **Implementation:** The lightweight FastAPI/Uvicorn server starts in milliseconds. It handles SIGTERM signals from Docker to shut down gracefully without dropping active connections.

### 10. Dev/Prod Parity 🟢 (Pass)
*Keep development, staging, and production as similar as possible.*
- **Implementation:** By utilizing Docker containers, the exact same OS layer, Python runtime, and application code that runs on a developer's local machine runs in UAT, Stage, and Prod. The only difference is the environment variables injected at runtime.

### 11. Logs 🟢 (Pass)
*Treat logs as event streams.*
- **Implementation:** The application does not attempt to write or manage log files on disk. Instead, it uses a structured `JSONFormatter` to stream all access, error, and audit logs directly to `stdout`. The container runtime (Docker) captures this stream, allowing it to be forwarded to external log aggregators.

### 12. Admin Processes 🟢 (Pass)
*Run admin/management tasks as one-off processes.*
- **Implementation:** The repository includes an `automation/` directory containing bash scripts for one-off administrative tasks (e.g., Key Vault provisioning, Ed25519 key generation) which run in identical environments to the main application setup.

---

### Conclusion
The `codexrelic.com` backend strictly adheres to all 12 principles of the 12-Factor App methodology. It is highly portable, completely stateless, and ready to be scaled horizontally in any modern container orchestration environment.
