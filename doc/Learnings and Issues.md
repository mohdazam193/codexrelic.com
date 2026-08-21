# System Architecture & CI/CD Learnings

## 1. 12-Factor App State Storage
We successfully migrated from an anti-pattern (storing state locally on the container filesystem via `resume.tex`) to a 12-Factor App compliant architecture using **OCI Object Storage** (S3 compatible). 
- **The "Why"**: Storing state inside the container means the data is lost whenever the container restarts, fails to persist across scaled replicas, and violates the "Stateless Processes" methodology.
- **The Solution**: We integrated `boto3` into FastAPI to stream uploads directly to Oracle Cloud Object Storage, making the application fully stateless and infinitely scalable.

## 2. Environment Bifurcation in S3
Instead of creating dozens of buckets for different environments and asset types, we organized a single bucket (`codexrelic-storage`) using folder prefixes. 
- **Implementation**: The pipeline injects an `APP_ENV` variable (e.g., `uat`, `prod`). The backend dynamically routes files to `{APP_ENV}/resume/...`.
- **Benefit**: This allows all environments to share a single bucket configuration without data overlap.

## 3. Azure Pipeline Templating (DRY Principle)
We refactored our Azure DevOps release pipeline from a massive, repetitive ~280-line file down to a clean ~40-line file using YAML templates.
- **The "Why"**: Defining deployment steps three times (UAT, Stage, Prod) means any bug fix or pipeline update requires changing three different places, leading to configuration drift.
- **The Solution**: We abstracted the logic into `templates/deploy-stage.yml` which accepts parameters like `environmentName`, `namespace`, and `keyVaultName`.

## 4. Centralized vs Environment Key Vaults
- We kept environment-specific variables (like MongoDB credentials) in environment-specific Key Vaults (`kv-uat-codexrelic`, `kv-stage-codexrelic`, etc.).
- We consolidated shared variables (like AWS S3 credentials) into a single, global Key Vault (`kv-aws-s3`). 
- **Benefit**: The pipeline seamlessly merges secrets from multiple Key Vaults just before creating the Kubernetes `.env` file, meaning we don't have to duplicate the same AWS credentials across 3 separate vaults.
