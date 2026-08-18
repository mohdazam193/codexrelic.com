# Pipeline Troubleshooting Guide

This guide covers common issues you might encounter while running the Azure DevOps pipelines and how to resolve them.

---

## 1. Release Pipeline Does Not Trigger Automatically
**Symptom:** The Build pipeline finishes successfully, but the Release pipeline doesn't start.
**Root Cause:** The `source` trigger in the Release YAML doesn't perfectly match the name of the Build pipeline in Azure DevOps.
**Fix:**
1. Check the exact name (and folder) of your Build pipeline in Azure DevOps.
2. Open `ci-cd/docker/azure-pipelines-release.yml`.
3. Update the `source:` parameter under `resources.pipelines` to match exactly (e.g., `\Build\Code Build Pipelines`).

---

## 2. Authorization Errors (Service Connections)
**Symptom:** The pipeline fails immediately with an error like: `The pipeline is not valid. Job Deploy: Step AzureKeyVault input connectedServiceName requires a service connection.`
**Root Cause:** The pipeline is trying to use a Service Connection (Key Vault, DockerHub, SSH, Snyk) that hasn't been authorized for this specific pipeline yet.
**Fix:**
1. Open the failed pipeline run in Azure DevOps.
2. Look for a message at the top saying "This pipeline needs permission to access a resource".
3. Click the **View** or **Authorize Resources** button and grant permission.

---

## 3. SSH Copy / Deployment Fails (Timeout)
**Symptom:** The `CopyFilesOverSSH` or `SSH` task hangs and then times out after 20000ms.
**Root Cause:** The Azure DevOps agent cannot reach your OCI VM.
**Fix:**
1. Ensure your OCI VM is running.
2. Ensure the VM's Public IP hasn't changed. If it has, update the `oci-vm-ssh` Service Connection in Azure DevOps.
3. Verify that the OCI Virtual Cloud Network (VCN) Security List allows inbound SSH (Port 22) traffic from `0.0.0.0/0`.

---

## 4. Kubernetes: ImagePullBackOff
**Symptom:** The pipeline says it applied the manifests, but when you check the VM, the pods aren't running and say `ImagePullBackOff`.
**Root Cause:** Kubernetes cannot pull your image from DockerHub. Either the image tag is wrong, or the repository is private and Kubernetes lacks the credentials.
**Fix:**
1. Verify the Build pipeline successfully pushed the image to DockerHub.
2. If the DockerHub repository is **private**, you must create a Kubernetes Secret containing your Docker registry credentials and add `imagePullSecrets` to your `deployment.yaml`. (If it is public, this is not an issue).

---

## 5. DevSecOps: TruffleHog Fails the Build
**Symptom:** The `Run TruffleHog Secret Scan` task fails and turns red.
**Root Cause:** TruffleHog found a hardcoded secret (like a password, API key, or private key) committed to the Git repository.
**Fix:**
- If we are running in "Audit Only" mode (using `--fail=false`), the task shouldn't fail the build. If it does, ensure the `--fail=false` flag is present in `ci-cd/docker/azure-pipelines-build.yml`.
- If you *want* it to fail to protect your code, you must remove the secret from the repository history or add it to a TruffleHog ignore file.

---

## 6. Snyk Fails the Build
**Symptom:** The pipeline fails during the Snyk Container or Snyk Code scan.
**Root Cause:** High-severity vulnerabilities were detected.
**Fix:**
- **Code:** Review the Snyk logs to see which dependency or line of code is vulnerable. Update the dependency version in `package.json` or `requirements.txt`.
- **Container:** The base image (e.g., `node:18-alpine` or `python:3.11`) might have an OS-level vulnerability. Update your `Dockerfile` to use a newer base image patch.
- **Bypass (Not Recommended):** If you must deploy immediately, you can temporarily set `failOnIssues: false` in the pipeline YAML.

---

## 7. Azure Key Vault Secrets Missing
**Symptom:** The deployment succeeds, but the application crashes immediately. Logs show missing environment variables (like `MONGO_URI`).
**Root Cause:** The `AzureKeyVault@2` task failed to pull the secrets, or the names of the secrets in the Key Vault don't match the `SecretsFilter` in the pipeline.
**Fix:**
1. Go to Azure Portal -> Your Key Vault.
2. Verify the secrets exist and are spelled exactly as they are in the pipeline (`MONGO-URI`, `JWT-SECRET`, etc.).
3. Ensure the Azure DevOps Service Principal has "Key Vault Secrets User" role access to that specific Key Vault.
