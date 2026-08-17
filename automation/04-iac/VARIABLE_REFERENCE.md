# Terraform Pipeline Variable Reference

This document is the **source of truth** for every variable required in the
Azure DevOps `terraform` Variable Group to run the IaC pipeline.

To set these up automatically, just run:
```bash
bash automation/04-iac/bootstrap-pipeline-variables.sh
```

---

## Required Variables

### OCI Authentication

| Variable Name | Description | Secret? | Example Value |
|---|---|---|---|
| `TF_VAR_tenancy_ocid` | Your OCI Tenancy OCID | No | `ocid1.tenancy.oc1..aaa...` |
| `TF_VAR_user_ocid` | Your OCI User OCID | No | `ocid1.user.oc1..aaa...` |
| `TF_VAR_fingerprint` | Fingerprint of the Terraform API signing key | No | `58:c1:5f:98:...` |
| `TF_VAR_region` | Your OCI region | No | `ap-hyderabad-1` |
| `TF_VAR_compartment_id` | OCID of the compartment to deploy into | No | `ocid1.tenancy.oc1..aaa...` |
| `TF_VAR_availability_domain` | The availability domain for the VM | No | `NjdN:AP-HYDERABAD-1-AD-1` |
| `TF_VAR_ssh_public_key` | SSH public key to inject into the VM | No | `ssh-ed25519 AAAA... codexrelic-admin` |
| `OCI_PRIVATE_KEY_B64` | Base64-encoded OCI API signing private key (unencrypted RSA) | **YES** | `LS0tLS1CRUdJT...` |

### OCI S3 State Backend

| Variable Name | Description | Secret? | Example Value |
|---|---|---|---|
| `TF_STATE_BUCKET` | OCI Object Storage bucket name | No | `codexrelic-tf-state` |
| `TF_STATE_ENDPOINT` | OCI S3-compatible endpoint URL | No | `https://axavxdm4dxfu.compat.objectstorage.ap-hyderabad-1.oraclecloud.com` |
| `TF_STATE_ACCESS_KEY` | OCI Customer Secret Key ID (access key) | No | `13dc2593...` |
| `TF_STATE_SECRET_KEY` | OCI Customer Secret Key value | **YES** | `MFqHFgl/L1W...` |

---

## How the Private Key Works

The OCI API private key is a multiline RSA PEM file. Azure DevOps
corrupts multiline environment variables by stripping newlines. To
work around this, we:

1. Generate a **fresh, unencrypted** RSA key dedicated to CI/CD.
2. Base64-encode it into a single-line string: `OCI_PRIVATE_KEY_B64`.
3. In the pipeline, decode it to a temp file at runtime:
   ```bash
   echo "$OCI_PRIVATE_KEY_B64" | base64 --decode > /tmp/oci_api_key.pem
   ```

> ⚠️ **Never use your personal encrypted OCI key in a pipeline.**
> Always generate a dedicated unencrypted key and register it
> separately in OCI Console under User → API Keys.

---

## Corresponding Terraform Variables

These map 1:1 to variables defined in `iac/oci/variables.tf`:

| Azure DevOps Variable | Terraform Variable | Notes |
|---|---|---|
| `TF_VAR_tenancy_ocid` | `tenancy_ocid` | Auto-picked up by Terraform via `TF_VAR_` prefix |
| `TF_VAR_user_ocid` | `user_ocid` | Auto-picked up |
| `TF_VAR_fingerprint` | `fingerprint` | Auto-picked up |
| `TF_VAR_region` | `region` | Auto-picked up |
| `TF_VAR_compartment_id` | `compartment_id` | Auto-picked up |
| `TF_VAR_availability_domain` | `availability_domain` | Auto-picked up |
| `TF_VAR_ssh_public_key` | `ssh_public_key` | Auto-picked up |
| `OCI_PRIVATE_KEY_B64` | `private_key_path` | Decoded to `/tmp/oci_api_key.pem`; path set via `TF_VAR_private_key_path` in pipeline |
