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
