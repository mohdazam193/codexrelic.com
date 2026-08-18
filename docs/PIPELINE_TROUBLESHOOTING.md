# Pipeline Troubleshooting Guide

This guide covers real issues encountered while running the Azure DevOps pipelines for this project, along with their resolutions.

## 1. TruffleHog Fails with `lstat false: no such file or directory`

**Symptom:** The `Run TruffleHog Secret Scan` task fails and turns red. The logs show:
```
error trufflehog encountered errors during scan {"job": 1, "source_name": "trufflehog - filesystem", "errors": ["lstat false: no such file or directory"]}
##[error]Bash exited with code '183'.
```

**Root Cause:** The TruffleHog command was executed with `--fail=false`. TruffleHog v3 treats `--fail` as a boolean flag that takes no arguments. Because of the `=false`, it attempted to treat `false` as a directory path to scan, which didn't exist, causing an `lstat` error.

**Fix:** 
To run TruffleHog in "Audit Only" mode without crashing the pipeline, we removed the `--fail=false` flag and instead used standard bash OR logic (`||`) to catch the non-zero exit code:
```yaml
trufflehog filesystem . || echo "Secrets found, but continuing build."
```

## 2. Snyk Fails with `FATAL No supported files found (SNYK-CLI-0008)`

**Symptom:** The Snyk Security Scan task fails with the following log:
```
FATAL No supported files found (SNYK-CLI-0008)
Could not detect supported target files in /home/vsts/work/1/s.
```

**Root Cause:** Snyk is running an application scan (`testType: 'app'`) which looks for dependency manifest files like `package.json` or `requirements.txt`. Because our Python application source code is nested inside the `src/` folder, Snyk fails to find the manifest at the root of the repository.

**Fix:** 
We explicitly passed the `targetFile` input to the Snyk Azure DevOps task to point it directly to the manifest:
```yaml
    - task: SnykSecurityScan@1
      inputs:
        targetFile: 'src/requirements.txt'
```

---

## 3. Snyk Fails with `ERROR Missing required packages (SNYK-OS-PYTHON-0013)`

**Symptom:** Snyk crashes during the application dependency scan with:
```
ERROR Missing required packages (SNYK-OS-PYTHON-0013)
Missing required packages
Status: 422 Unprocessable Entity
```

**Root Cause:** Snyk uses the local environment's Python to analyze and build the dependency tree from `requirements.txt`. If the packages listed in `requirements.txt` are not actually installed in the pipeline runner's environment, Snyk cannot resolve them and fails the scan.

**Fix:**
We added a script step to install the Python dependencies *before* the Snyk task runs.
```yaml
    - script: |
        python3 -m pip install -r src/requirements.txt
      displayName: 'Install Dependencies for Snyk SCA'
```

---

## 4. Snyk Fails with `ERROR Authentication error (SNYK-0005)`

**Symptom:** The Snyk task fails with a `401 Unauthorized` status:
```
ERROR   Authentication error (SNYK-0005)
Authentication credentials not recognized, or user access is not provisioned.
Status:  401 Unauthorized
```

**Root Cause:** The pipeline is trying to authenticate with Snyk using a Service Connection, but the connection doesn't exist, is misspelled, or doesn't have a valid API token attached to it. (We also had a typo in the pipeline variable where it was spelled `Synk`).

**Fix:**
1. Log into your [Snyk Dashboard](https://app.snyk.io/) and generate an API Token (Account Settings -> General -> API Token).
2. Go to **Azure DevOps -> Project Settings -> Service Connections**.
3. Create a **New Service Connection**, search for **Snyk**, and paste your API token.
4. Name the connection exactly **`Snyk`**.
5. Re-run the pipeline. The `snykServiceConnection` variable in the pipeline is now correctly pointing to `Snyk` to match this connection.

---

## 5. Snyk Fails with `High severity vulnerability found in ...` (Container Scan)

**Symptom:** The Snyk Container Vulnerability Scan fails the pipeline and outputs logs like:
```
✗ High severity vulnerability found in attr/libattr1
Base Image python:3.11-slim 73 vulnerabilities (0 critical, 2 high, 2 medium, 69 low)
##[error]failing task because `snyk test` found issues
```

**Root Cause:** Snyk scanned the compiled Docker image and found that the underlying operating system inside the base image (`python:3.11-slim` running Debian) has unpatched high-severity CVEs (like `libattr1`). Because our pipeline enforces a `severityThreshold: 'high'`, Snyk intentionally blocks the deployment to protect the environment.

**Fix:**
We updated `docker/Dockerfile` to use a significantly smaller, more secure base image (Alpine Linux) which contains fewer OS utilities and therefore far fewer vulnerabilities:
```diff
- FROM python:3.11-slim
+ FROM python:3.11-alpine
```
