terraform {
  required_providers {
    oci = {
      source  = "oracle/oci"
      version = "~> 5.0"
    }
  }

  backend "s3" {
    # OCI Object Storage S3-compatible backend
    # All config injected at runtime via terraform init -backend-config flags
    skip_region_validation      = true
    skip_credentials_validation = true
    skip_requesting_account_id  = true
    use_path_style              = true
    force_path_style            = true
    skip_sso_auth               = true
    skip_metadata_api_check     = true
  }
}

provider "oci" {
  tenancy_ocid = var.tenancy_ocid
  user_ocid    = var.user_ocid
  fingerprint  = var.fingerprint
  # Key is written to a temp file by the pipeline from a base64-encoded secret.
  # This avoids newline corruption when passing PEM content through env vars.
  private_key_path = var.private_key_path
  region           = var.region
}
