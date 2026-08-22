# Learnings and Issues Encountered

This is a living document tracking the timeline of architectural decisions, issues encountered, and how they were resolved during the deployment of `codexrelic.com`.

## Timeline

### 2026-08-17: Infrastructure as Code (IaC) Migration

**Goal:** Provision an OCI (Oracle Cloud Infrastructure) Ampere A1 VM and automate the deployment using Terraform inside an Azure DevOps Pipeline.

#### Issue 1: Azure Service Principal Authentication in Terraform
- **What Happened:** We initially tried to store the Terraform state file (`terraform.tfstate`) in an Azure Storage Account. The Azure DevOps pipeline was running under a Service Principal and authenticated using the `AzureCLI@2` task.
- **The Error:** Terraform's `azurerm` backend crashed with `Authenticating using the Azure CLI is only supported as a User (not a Service Principal)`.
- **The Learning:** Terraform's Azure provider explicitly blocks Service Principals from hooking into the Azure CLI's active session for security reasons. We had to pass the Service Principal credentials explicitly via environment variables (`ARM_CLIENT_ID`, `ARM_CLIENT_SECRET`, etc.) and explicitly disable CLI auth (`ARM_USE_AZURECLI=false`).

#### Decision: Migrate State File to OCI Object Storage
- **The Pivot:** Because dealing with Azure RM state auth inside Azure DevOps was brittle, and to keep all infrastructure components localized to Oracle Cloud, we decided to migrate the state file entirely to an OCI Object Storage bucket using Terraform's S3-compatible API.
- **Automation:** We wrote a Bash script (`automation/04-iac/setup-oci-backend.sh`) that successfully used the local `oci` CLI to automatically generate the S3 Customer Secret Keys.

#### Issue 2: Bash Variable Injection vs Azure DevOps Macros
- **What Happened:** When running `terraform init` with the new OCI S3 variables, the pipeline crashed complaining about missing region parameters.
- **The Error:** We were using bash interpolation `${TF_VAR_region}` in the pipeline script. Azure DevOps automatically injects pipeline variables as **UPPERCASE** environment variables (`$TF_VAR_REGION`). Since bash is case-sensitive, the variable evaluated to an empty string.
- **The Fix:** Switched from bash variables to native Azure DevOps Macros `$(TF_VAR_region)`. The Azure pipeline agent evaluates macros and replaces the text directly in the script *before* Bash even runs, bypassing case-sensitivity issues completely.

#### Issue 3: OCI Object Storage SSL Certificate Wildcards
- **What Happened:** The pipeline triggered successfully with the variables, but `terraform plan` failed.
- **The Error:** `x509: certificate is valid for swiftobjectstorage... but not codexrelic-tf-state...`. 
- **The Learning:** OCI's S3-compatible endpoints use a single-level wildcard SSL certificate. By default, Terraform's S3 module tries to use "Virtual Hosted-Style" URLs (`https://<bucket_name>.<endpoint>`), which creates a second-level subdomain that breaks the SSL verification.
- **The Fix:** Added `force_path_style = true` to the `backend "s3"` block in `provider.tf`. This forces Terraform to put the bucket name in the path (`https://<endpoint>/<bucket_name>`), keeping the domain at one level and perfectly matching the OCI SSL certificate.

#### Issue 4: Terraform Hanging for 50+ Minutes (Missing Variables)
- **What Happened:** The pipeline ran but hung silently for over 50 minutes.
- **The Root Cause:** Terraform was waiting for interactive user input on the command line for missing variables. In a CI/CD environment, nobody is there to type, so it hung forever.
- **The Fix:** Added `-input=false` to all `terraform init`, `plan`, and `apply` commands. This makes Terraform immediately error out instead of hanging when variables are missing, giving a clear diagnostic message.
- **Best Practice:** Always use `-input=false` in CI/CD pipelines.

#### Issue 5: Variable Group Variables Not Available in Bash
- **What Happened:** Even after adding variables to the Azure DevOps Variable Group, Terraform still reported them as missing.
- **The Root Cause:** Azure DevOps does NOT automatically export Variable Group variables as shell environment variables. They are only available as YAML macros (`$(VAR_NAME)`) inside the pipeline YAML itself. The bash script running inside the agent has no visibility of them unless explicitly mapped.
- **The Fix:** Added an explicit `env:` block to every pipeline `script` step, manually mapping each variable from the YAML macro context into the bash environment.
- **Pattern:**
  ```yaml
  - script: |
      echo $MY_VAR  # This works ONLY because of the env: block below
    env:
      MY_VAR: $(MY_VAR)  # This is the required mapping
  ```

#### Issue 6: OCI Provider Failing with Encrypted Private Key
- **What Happened:** After all variables were properly injected, the Terraform OCI provider still failed to authenticate.
- **The Error:** `did not find a proper configuration for private key`.
- **The Root Cause:** The OCI API signing key stored in `~/.oci/` was encrypted with a passphrase (`BEGIN ENCRYPTED PRIVATE KEY`). The Terraform OCI provider cannot use passphrase-protected keys without explicitly providing the password. Additionally, Azure DevOps corrupts multiline PEM content when injecting it as environment variables — newlines get stripped, making the key unparseable regardless.
- **The Fix (Two-Part):**
  1. Generated a **fresh, unencrypted RSA 2048 key** dedicated to Terraform/CI-CD use. Never use your personal OCI key (which may be encrypted) in a pipeline.
  2. Stored the private key as **base64-encoded** in Azure DevOps (`OCI_PRIVATE_KEY_B64`). In the pipeline, we decode it back to a file: `echo "$OCI_PRIVATE_KEY_B64" | base64 --decode > /tmp/oci_api_key.pem`. This sidesteps the newline corruption problem entirely.
- **Key Lesson:** Never try to pass PEM/multiline secrets directly as environment variables. Always base64-encode them first.

#### Issue 7: Terraform Provider Binary Permission Denied in Apply Stage
- **What Happened:** The Plan stage succeeded and the Approval gate was passed, but the Apply stage failed immediately.
- **The Error:** `fork/exec .terraform/providers/.../terraform-provider-oci_v5.47.0: permission denied`
- **The Root Cause:** When Azure DevOps publishes an artifact (at the end of Plan stage), it **intentionally strips the executable (`+x`) permission bit** from all files for security reasons. When the Apply stage downloads the artifact, the Terraform provider binaries are present but no longer executable.
- **The Fix:** Added a dedicated step immediately after the artifact download that restores the execute bit on all provider binaries:
  ```bash
  find $(Pipeline.Workspace)/TerraformPlan/.terraform -type f \
    -name "terraform-provider-*" -exec chmod +x {} \;
  ```
- **Key Lesson:** Any time you pass compiled binaries between Azure DevOps pipeline stages via artifacts, you must explicitly restore their executable permissions. This applies to Terraform providers, Go binaries, compiled CLIs — anything that needs to be executed.

#### Issue 8: OCI "Out of Host Capacity" for Always Free ARM Instances
- **What Happened:** The Terraform Apply stage succeeded technically (auth, state, etc.) but failed when actually creating the VM.
- **The Error:** `500-InternalError, Out of host capacity.` from OCI's `LaunchInstance` API.
- **The Root Cause:** Oracle's Always Free Ampere A1 (ARM) VMs are extremely popular globally. OCI frequently runs out of free-tier capacity in a given region/availability domain. This is **not a code bug** — it is OCI telling you "there are no free ARM slots available right now, try again later."
- **The Fix:** Added an automatic retry loop to the Apply stage. It retries `terraform apply` every 5 minutes for up to 100 minutes (20 attempts), cycling through all 3 fault domains.

#### Issue 9: OCI Free Tier Region Limitations
- **What Happened:** We attempted to switch regions to find better Always Free capacity, but the OCI console blocked the region subscription.
- **The Root Cause:** OCI strictly limits Free Tier accounts to their **home region**. You cannot subscribe to additional regions unless you upgrade to a Pay-As-You-Go (PAYG) account. Even if you upgrade to PAYG, the Always Free ARM limits (4 OCPUs, 24GB RAM) **only apply to your home region**. If you deploy them elsewhere, you will be billed.
- **The Lesson:** When on the Free Tier, you must stay in your home region and rely on the automated Terraform retry loop to eventually acquire capacity. Alternatively, upgrading to PAYG gives your account priority access to capacity in your home region, while still remaining free (as long as you stay within the 4 OCPU / 24GB limit).

### 2026-08-18: Server Access & Kubernetes Setup

#### Learning 10: Accessing the Provisioned OCI VM
- **The Context:** Once the Terraform apply finishes and the `codexrelic-vm` is created, you need to access it securely.
- **The Connection:** The VM is provisioned with an Ubuntu image and assigned a Public IP. Authentication is strictly via the ED25519 SSH private key we generated earlier.
- **The Command:** To connect locally from your machine:
  ```bash
  ssh -i ~/.ssh/codexrelic_ed25519 ubuntu@<PUBLIC_IP>
  ```
  *(In our case, the current Public IP is `129.225.82.233`)*

### 2026-08-18: DevSecOps Integration

**Goal:** Integrate automated security scanning across the Infrastructure and Application pipelines.

#### Implementation 1: Checkov for Infrastructure as Code (IaC)
- **What We Did:** Added Checkov to the `azure-pipelines-iac.yml` pipeline right before `terraform plan`.
- **The Value:** Checkov statically analyzes Terraform code (`iac/oci/`) to ensure no cloud misconfigurations are deployed (e.g., leaving a subnet open to the internet, missing encryption). It acts as a preventative security gate.

#### Implementation 2: TruffleHog for Secret Scanning
- **What We Did:** Integrated TruffleHog into `azure-pipelines-build.yml` in "Audit Only" mode.
- **The Value:** TruffleHog scans the repository history to find accidentally committed API keys, passwords, and tokens. Running it in audit mode warns developers without hard-failing the build, but creates a visible security signal.

#### Implementation 3: Snyk Code for Static Application Security Testing (SAST)
- **What We Did:** Added Snyk Code (`testType: 'app'`) to the Build pipeline.
- **The Value:** Snyk Code scans the actual source code (Python, JS) for application-level vulnerabilities like SQL Injection, Cross-Site Scripting (XSS), and insecure dependencies *before* the Docker image is even built.

#### Issue 11: Snyk Container Scan Failing on Base Image Vulnerabilities
- **What Happened:** The Snyk Container scan step successfully ran but intentionally failed the build.
- **The Error:** `✗ High severity vulnerability found in attr/libattr1 ... Image layer: Introduced by your base image (python:3.11-slim)`.
- **The Root Cause:** We enforced `failOnIssues: true` with a `high` severity threshold. The underlying OS of the `python:3.11-slim` image (Debian) contained unpatched high-severity CVEs, so Snyk blocked the deployment to protect the environment.
- **The Fix:** We updated the `docker/Dockerfile` to use a significantly smaller, more secure base image: `FROM python:3.11-alpine`.

#### Issue 12: Docker Build Failing on Alpine (C Extensions)
- **What Happened:** After switching to `python:3.11-alpine`, the Docker build task started failing on `pip install`.
- **The Error:** Missing build dependencies like `gcc` or `Failed building wheel for cryptography / bcrypt`.
- **The Root Cause:** Alpine Linux uses `musl` libc instead of `glibc`. Pre-compiled Python wheels for packages with C extensions (like `bcrypt` and `cryptography`) often don't work out-of-the-box on Alpine. They require source compilation, but Alpine lacks the build tools natively.
- **The Fix:** Added the required Alpine build dependencies immediately before `pip install` in the `Dockerfile`:
  ```dockerfile
  RUN apk add --no-cache gcc musl-dev libffi-dev build-base
  ```

#### Issue 13: Pipeline Failing with "A task is missing" (Azure DevOps)
- **What Happened:** The pipeline failed immediately upon triggering.
- **The Error:** `A task is missing. The pipeline references a task called 'SynkSecurityScan'.`
- **The Root Cause:** During a global Find & Replace inside the Azure DevOps web portal to correct a Service Connection name, the official task name `SnykSecurityScan@1` was accidentally misspelled as `SynkSecurityScan@1`. Also, this change was only on the remote repo and caused the remote and local branches to diverge.
- **The Fix:** Pulled the remote changes using `git pull --rebase`, corrected the YAML task back to `SnykSecurityScan@1`, committed, and pushed to both Github and Azure DevOps remotes to re-sync everything.

### 2026-08-18: Application Deployment Troubleshooting

#### Issue 14: Docker Push "Denied" due to Placeholder Name
- **What Happened:** The Build and Scan steps passed, but the pipeline failed on the `Push Docker Image to DockerHub` step.
- **The Error:** `denied: requested access to the resource is denied`
- **The Root Cause:** The pipeline variable `imageName` was still set to the default placeholder: `yourusername/codexrelic-api`. The pipeline tried to push to `docker.io/yourusername/...` using the developer's credentials. Docker Hub rejected it because the developer doesn't own the namespace `yourusername`.
- **The Fix:** Updated the pipeline variable `imageName` to use the actual Docker Hub username (`aazammohammad193/codexrelic-api`).

#### Issue 15: K3s Deployment Failing with "Permission Denied"
- **What Happened:** The Release pipeline connected to the VM via SSH, but all `kubectl` commands failed.
- **The Error:** `error: error loading config file "/etc/rancher/k3s/k3s.yaml": open /etc/rancher/k3s/k3s.yaml: permission denied`
- **The Root Cause:** By default, K3s provisions its config file (`/etc/rancher/k3s/k3s.yaml`) with root-only read permissions (`600`). The SSH task was connecting as the unprivileged `ubuntu` user.
- **The Fix:** Updated the deployment pipeline script to prefix all `kubectl` commands with `sudo`. Since the `ubuntu` user has passwordless sudo access, this bypasses the permission issues securely without modifying K3s defaults.

#### Issue 16: ImagePullBackOff in Kubernetes due to Release Pipeline Placeholder
- **What Happened:** The Release pipeline finally succeeded in applying the manifests to K3s (bypassing the permission denied error), but the pod failed to start.
- **The Error:** `Failed to pull image "yourusername/codexrelic-api:56": ... pull access denied`
- **The Root Cause:** We previously updated the `imageName` variable with the real Docker Hub username (`aazammohammad193`) in the **Build pipeline**, but the **Release pipeline** (`azure-pipelines-release.yml`) had its own separate `variables` block that was still using the `yourusername/codexrelic-api` placeholder.
- **The Fix:** Updated the `imageName` variable in `azure-pipelines-release.yml` to match the build pipeline (`aazammohammad193/codexrelic-api`).

#### Issue 17: Pod CrashLoopBackOff due to CPU Architecture Mismatch (exec format error)
- **What Happened:** The pod finally pulled the correct image (`:58`), created the container, and started it. However, the container immediately crashed on startup, triggering a `CrashLoopBackOff` loop.
- **The Error:** While no explicit error logs were immediately visible, the container was instantly exiting.
- **The Root Cause:** The Azure DevOps build agent (`ubuntu-latest`) runs on a standard **x86_64 (AMD64)** processor, so Docker natively builds an AMD64 image. However, the target Kubernetes cluster runs on an Oracle Cloud Always Free Ampere A1 VM, which is an **ARM64** processor. Running an AMD64 container on an ARM64 host without emulation causes an instant `exec format error` crash at the kernel level.
- **The Fix:** We updated the `azure-pipelines-build.yml` to explicitly build a cross-compiled ARM64 image using QEMU. 
  1. We added a script step before the Docker build to register QEMU: `docker run --rm --privileged multiarch/qemu-user-static --reset -p yes`.
  2. We passed `arguments: '--platform linux/arm64'` to the `Docker@2` build task to force it to build an ARM-native image that can run seamlessly on the OCI VM.

### 2026-08-18: Zero-Downtime SSL Automation

#### Learning 18: Automated SSL Certificates with cert-manager
- **The Goal:** Automate the provisioning and 30-day rotation of Let's Encrypt SSL certificates for `uat.codexrelic.com`, `stage`, and `api` endpoints.
- **The Implementation:** Instead of building a complex custom pipeline to rotate certificates, we leveraged **cert-manager**, the industry standard Kubernetes operator for TLS. 
- **The Setup:** 
  1. We added a step in the Release pipeline to automatically install `cert-manager` and deploy a Let's Encrypt `ClusterIssuer`.
  2. We created a base `ingress.yaml` template with Traefik routing rules and `DOMAIN_PLACEHOLDER`.
  3. During the release pipeline, we use `sed` to dynamically inject the correct domain (e.g., `uat.codexrelic.com`) into the Ingress manifest before applying it.
  4. To enforce strict 30-day rotation, we added the annotation `cert-manager.io/renew-before: "1440h"` (60 days) to the Ingress. Since Let's Encrypt certificates are valid for 90 days, this forces cert-manager to negotiate a brand new certificate exactly every 30 days autonomously.

#### Learning 19: Weekly SSL Health Monitoring
- **The Goal:** Ensure visibility into the autonomous SSL rotation process.
- **The Implementation:** We created a secondary Azure Pipeline (`azure-pipelines-ssl-check.yml`) configured with a weekly cron schedule (`cron: "0 0 * * 0"`). This pipeline connects to the cluster and executes a script to parse the `Ready` status of all certificates via `kubectl get certificates -A -o jsonpath=...`. If any certificate fails to renew, the pipeline fails and alerts the team.

### 2026-08-22: Observability & Auto-Scaling

#### Learning 20: Lightweight OpenObserve Integration
- **The Goal:** Add comprehensive observability (Logs and Metrics) to the Kubernetes cluster using OpenObserve, without overwhelming the limited resources of the Oracle Cloud Free Tier VM.
- **The Issue:** The official OpenObserve Helm chart is designed for massive enterprise clusters. Out of the box, it attempts to install heavy Kubernetes Operators (like CloudNativePG for PostgreSQL and Prometheus Operators for metrics) which failed to deploy because the CRDs were missing, and more importantly, would have consumed too much RAM/CPU on our small VM.
- **The Design Choice (Fix):** We customized the Helm deployment values to forcefully disable these heavy dependencies and run OpenObserve in its most lightweight configuration:
  1. `postgres.enabled=false` and `config.ZO_LOCAL_MODE="true"`: Bypasses the need for a complex PostgreSQL operator, instructing OpenObserve to use its lightweight embedded metadata store (Sled/SQLite) while still pushing long-term logs to our S3 bucket.
  2. `opentelemetry-operator.enabled=false`: Instructs the OpenObserve Collector to run as a simple, lightweight DaemonSet rather than attempting to inject OpenTelemetry CRDs across the entire cluster.
  3. `config.ZO_COMPACT_DATA_RETENTION_DAYS="5"`: Enforced a strict 5-day retention policy to ensure we don't rack up infinite S3 storage costs.
- **The Result:** We achieved a fully functional, highly efficient observability stack that fits perfectly within the constraints of a Free Tier VM.


#### Issue 22: Helm CLI Missing on Deployment VM
- **What Happened:** When deploying OpenObserve, the pipeline failed with `helm: command not found`.
- **The Root Cause:** The Oracle Cloud VM was running K3s, which comes with `kubectl`, but it did not have the `helm` CLI installed natively. Because the deployment pipeline connects to the VM via SSH to execute commands locally, it could not execute the Helm charts.
- **The Fix:** Added a robust `if ! command -v helm &> /dev/null` check inside the deployment script (`azure-pipelines-release.yml`) that automatically downloads and installs the Helm CLI binary prior to attempting any `helm upgrade` commands.

#### Issue 23: cert-manager Ignoring OpenObserve Ingress (Red Certificate)
- **What Happened:** OpenObserve successfully deployed, but the HTTPS certificate for the `observDomain` (e.g., `stage-observ.codexrelic.com`) was invalid (showing a red warning in the browser).
- **The Root Cause:** The OpenObserve Helm chart defaults to using `className: "nginx"` for its Ingress. However, the K3s cluster uses **Traefik** as its ingress controller. Because the Ingress class didn't match `traefik`, `cert-manager` failed to spin up the HTTP01 ACME challenge solver pod, preventing Let's Encrypt from verifying the domain and issuing the certificate.
- **The Fix:** Explicitly set the ingress class to Traefik and added the required Traefik TLS annotations during the Helm installation:
  - `--set ingress.className="traefik"`
  - `--set ingress.annotations."traefik\.ingress\.kubernetes\.io/router\.entrypoints"="websecure"`
  - `--set ingress.annotations."traefik\.ingress\.kubernetes\.io/router\.tls"="true"`

