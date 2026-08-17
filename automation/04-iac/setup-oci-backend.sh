#!/usr/bin/env bash
# ============================================================
# 04-iac/setup-oci-backend.sh
# Automates: Creating OCI Object Storage for Terraform State
#
# What this does:
#   - Creates an OCI Object Storage bucket
#   - Generates an S3-compatible Customer Secret Key for your user
#   - Outputs the exact variables for your Azure DevOps pipeline
#
# Usage:
#   bash automation/04-iac/setup-oci-backend.sh
# ============================================================

set -euo pipefail

RED='\033[0;31m'; YELLOW='\033[1;33m'; GREEN='\033[0;32m'; CYAN='\033[0;36m'; NC='\033[0m'

echo -e "${CYAN}============================================================${NC}"
echo -e "${CYAN}  codexrelic.com — OCI Terraform State Setup               ${NC}"
echo -e "${CYAN}============================================================${NC}"

if ! command -v oci &>/dev/null; then
  echo -e "${RED}[ERROR] OCI CLI not found. Please install it first.${NC}"
  exit 1
fi

# Fetch namespace
echo -e "${CYAN}[1/4] Fetching OCI Namespace...${NC}"
NAMESPACE=$(oci os ns get --query "data" --raw-output)
echo "Namespace: $NAMESPACE"

# We need the user's Compartment OCID to create the bucket.
# We will use the tenancy OCID (root compartment) from the default config.
echo -e "${CYAN}[2/4] Fetching Configured Tenancy & User...${NC}"
TENANCY_OCID=$(grep -v '^#' ~/.oci/config | grep tenancy | head -1 | cut -d '=' -f 2)
USER_OCID=$(grep -v '^#' ~/.oci/config | grep user | head -1 | cut -d '=' -f 2)
REGION=$(grep -v '^#' ~/.oci/config | grep region | head -1 | cut -d '=' -f 2)

if [ -z "$TENANCY_OCID" ] || [ -z "$USER_OCID" ] || [ -z "$REGION" ]; then
  echo -e "${RED}[ERROR] Could not parse ~/.oci/config for tenancy, user, or region.${NC}"
  exit 1
fi

BUCKET_NAME="codexrelic-tf-state"

echo -e "${CYAN}[3/4] Creating Bucket: ${BUCKET_NAME}...${NC}"
# Check if bucket exists
if oci os bucket get --namespace-name "$NAMESPACE" --bucket-name "$BUCKET_NAME" &>/dev/null; then
  echo -e "${YELLOW}Bucket ${BUCKET_NAME} already exists. Skipping creation.${NC}"
else
  oci os bucket create \
    --namespace-name "$NAMESPACE" \
    --compartment-id "$TENANCY_OCID" \
    --name "$BUCKET_NAME" \
    --public-access-type "NoPublicAccess" \
    --versioning "Enabled" \
    --output none
  echo -e "${GREEN}Bucket created!${NC}"
fi

echo -e "${CYAN}[4/4] Generating Customer Secret Key...${NC}"
KEY_DISPLAY_NAME="terraform-state-$(date +%s)"
SECRET_JSON=$(oci iam customer-secret-key create \
  --user-id "$USER_OCID" \
  --display-name "$KEY_DISPLAY_NAME")

ACCESS_KEY=$(echo "$SECRET_JSON" | grep -o '"id": "[^"]*' | head -1 | cut -d'"' -f4)
SECRET_KEY=$(echo "$SECRET_JSON" | grep -o '"key": "[^"]*' | cut -d'"' -f4)

ENDPOINT="https://${NAMESPACE}.compat.objectstorage.${REGION}.oraclecloud.com"

echo -e "\n${GREEN}[DONE] OCI Object Storage Backend Successfully Created!${NC}"
echo -e "${YELLOW}Add the following 4 variables to your 'terraform' Variable Group in Azure DevOps:${NC}"
echo -e "------------------------------------------------------------"
echo -e "TF_STATE_BUCKET     = ${BUCKET_NAME}"
echo -e "TF_STATE_ENDPOINT   = ${ENDPOINT}"
echo -e "TF_STATE_ACCESS_KEY = ${ACCESS_KEY}"
echo -e "TF_STATE_SECRET_KEY = ${SECRET_KEY}"
echo -e "------------------------------------------------------------"
