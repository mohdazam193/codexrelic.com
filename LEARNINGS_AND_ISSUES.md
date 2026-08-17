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
- **The Fix:** Added an automatic retry loop to the Apply stage. It retries `terraform apply` every 5 minutes for up to 100 minutes (20 attempts). OCI typically frees up capacity within 30–60 minutes.
- **The Code:**
  ```bash
  MAX_RETRIES=20
  WAIT_SECONDS=300
  until terraform apply -auto-approve -input=false tfplan; do
    sleep $WAIT_SECONDS
    attempt=$((attempt + 1))
  done
  ```
- **Alternative:** If retrying for too long, try changing `TF_VAR_availability_domain` to a different AD in the same region, or switch to a different OCI region entirely.
