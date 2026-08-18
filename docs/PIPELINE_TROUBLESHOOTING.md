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
