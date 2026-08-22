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

## 5. Simplifying Auth: Database-Backed 3-Factor over WebCrypto Ed25519
We initially implemented a highly complex 3-factor authentication system using `Ed25519` cryptographic signatures via the browser's `Web Crypto API`, relying on a server-side memory challenge.
- **The Issue**: 
  - The in-memory challenge `_challenges = {}` failed when deployed to multiple Kubernetes pods (Pod A issued the challenge, Pod B failed to verify it).
  - The 30-second expiry was too tight for humans typing passwords and pasting keys.
  - Relying on `ADMIN_USER` and `ADMIN_PASS` as `.env` variables fails elegantly when a database connection is active but the `admin_users` table is empty.
- **The Solution**: We removed the `Ed25519` signature math and migrated to a **Database-Backed 3-Factor Authentication**. The user now submits `username`, `password`, and a `private_key` string over HTTPS. The backend securely checks all three using `bcrypt` hashes stored in MongoDB, ensuring multi-pod scalability, easier admin provisioning, and eliminating cryptographic timing bugs.
