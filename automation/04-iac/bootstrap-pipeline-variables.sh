#!/usr/bin/env bash
# ============================================================
# 04-iac/bootstrap-pipeline-variables.sh
#
# PURPOSE:
#   One-command setup for all Azure DevOps variable group
#   variables required to run the Terraform IaC pipeline.
#
# WHAT THIS DOES:
#   1. Reads your local ~/.oci/config to extract OCI values
#   2. Generates a fresh unencrypted RSA key for Terraform
#   3. Adds the key to OCI as an API key
#   4. Runs setup-oci-backend.sh to create the S3 state bucket
#   5. Creates/updates the Azure DevOps 'terraform' variable group
#      with all required variables automatically
#
# PRE-REQUISITES:
#   - `oci` CLI installed and configured (oci setup config)
#   - `az` CLI installed and logged in (az login)
#   - Azure DevOps extension: az extension add --name azure-devops
#
# USAGE:
#   bash automation/04-iac/bootstrap-pipeline-variables.sh
#
# ============================================================
set -euo pipefail

RED='\033[0;31m'; YELLOW='\033[1;33m'; GREEN='\033[0;32m'
CYAN='\033[0;36m'; BOLD='\033[1m'; NC='\033[0m'

# ── CONFIG ───────────────────────────────────────────────────
AZDO_ORG="https://dev.azure.com/codexrelic"
AZDO_PROJECT="codexrelic.com"
VARIABLE_GROUP_NAME="terraform"
TF_KEY_PATH="$HOME/.oci/codexrelic_terraform_key.pem"
TF_PUB_KEY_PATH="$HOME/.oci/codexrelic_terraform_key_public.pem"
# ─────────────────────────────────────────────────────────────

echo -e "${CYAN}${BOLD}"
echo "============================================================"
echo "  codexrelic.com — Pipeline Variable Bootstrap             "
echo "============================================================"
echo -e "${NC}"

# ── Step 0: Sanity checks ────────────────────────────────────
echo -e "${CYAN}[0/6] Checking prerequisites...${NC}"
for cmd in oci az openssl base64; do
  if ! command -v "$cmd" &>/dev/null; then
    echo -e "${RED}[ERROR] '$cmd' is not installed. Please install it first.${NC}"
    exit 1
  fi
done

# Ensure Azure DevOps extension is installed
if ! az extension show --name azure-devops &>/dev/null; then
  echo "Installing Azure DevOps CLI extension..."
  az extension add --name azure-devops -y
fi

az devops configure --defaults organization="$AZDO_ORG" project="$AZDO_PROJECT"
echo -e "${GREEN}[OK] All prerequisites met.${NC}"

# ── Step 1: Read OCI config ──────────────────────────────────
echo -e "${CYAN}[1/6] Reading OCI configuration...${NC}"
OCI_TENANCY=$(grep -v '^#' ~/.oci/config | grep tenancy | head -1 | cut -d'=' -f2 | tr -d ' ')
OCI_USER=$(grep -v '^#' ~/.oci/config | grep ^user | head -1 | cut -d'=' -f2 | tr -d ' ')
OCI_REGION=$(grep -v '^#' ~/.oci/config | grep ^region | head -1 | cut -d'=' -f2 | tr -d ' ')
OCI_NAMESPACE=$(oci os ns get --query "data" --raw-output)

# Availability domain — pick the first free-tier one
OCI_AD=$(oci iam availability-domain list \
  --compartment-id "$OCI_TENANCY" \
  --query "data[0].name" --raw-output)

echo "  Tenancy:    $OCI_TENANCY"
echo "  User:       $OCI_USER"
echo "  Region:     $OCI_REGION"
echo "  Namespace:  $OCI_NAMESPACE"
echo "  Avail Dom:  $OCI_AD"
echo -e "${GREEN}[OK] OCI config loaded.${NC}"

# ── Step 2: Generate unencrypted Terraform RSA key ───────────
echo -e "${CYAN}[2/6] Generating unencrypted Terraform API signing key...${NC}"
if [[ -f "$TF_KEY_PATH" ]]; then
  echo -e "${YELLOW}Key already exists at $TF_KEY_PATH. Skipping generation.${NC}"
else
  openssl genrsa -out "$TF_KEY_PATH" 2048 2>/dev/null
  openssl rsa -pubout -in "$TF_KEY_PATH" -out "$TF_PUB_KEY_PATH" 2>/dev/null
  chmod 600 "$TF_KEY_PATH"
  echo -e "${GREEN}[OK] Key generated at $TF_KEY_PATH${NC}"
fi

# Compute fingerprint and base64
TF_FINGERPRINT=$(openssl pkey -in "$TF_KEY_PATH" -pubout -outform DER 2>/dev/null | openssl dgst -md5 -c | awk '{print $2}')
TF_KEY_B64=$(base64 -i "$TF_KEY_PATH" | tr -d '\n')
TF_PUB_KEY_CONTENT=$(cat "$TF_PUB_KEY_PATH")
echo "  Fingerprint: $TF_FINGERPRINT"

# ── Step 3: Upload public key to OCI ─────────────────────────
echo -e "${CYAN}[3/6] Uploading new API key to OCI...${NC}"
# Check if already uploaded by fingerprint
EXISTING=$(oci iam api-key list --user-id "$OCI_USER" \
  --query "data[?fingerprint=='$TF_FINGERPRINT'].fingerprint" --raw-output 2>/dev/null || true)

if [[ -n "$EXISTING" ]]; then
  echo -e "${YELLOW}API Key with fingerprint $TF_FINGERPRINT already exists in OCI. Skipping.${NC}"
else
  oci iam api-key upload \
    --user-id "$OCI_USER" \
    --key "$TF_PUB_KEY_CONTENT" \
    --output none
  echo -e "${GREEN}[OK] API key uploaded to OCI.${NC}"
fi

# ── Step 4: Create OCI Object Storage bucket for state ───────
echo -e "${CYAN}[4/6] Setting up OCI Object Storage backend...${NC}"
bash "$(dirname "$0")/setup-oci-backend.sh" 2>/dev/null | tail -6

# Re-read the values for the state bucket
TF_STATE_BUCKET="codexrelic-tf-state"
TF_STATE_ENDPOINT="https://${OCI_NAMESPACE}.compat.objectstorage.${OCI_REGION}.oraclecloud.com"

# Generate a fresh S3 key specifically for this run
KEY_DISPLAY_NAME="terraform-state-bootstrap-$(date +%s)"
SECRET_JSON=$(oci iam customer-secret-key create \
  --user-id "$OCI_USER" \
  --display-name "$KEY_DISPLAY_NAME")
TF_STATE_ACCESS_KEY=$(echo "$SECRET_JSON" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['data']['id'])")
TF_STATE_SECRET_KEY=$(echo "$SECRET_JSON" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['data']['key'])")
echo -e "${GREEN}[OK] State backend ready.${NC}"

# ── Step 5: Get or create Azure DevOps variable group ────────
echo -e "${CYAN}[5/6] Setting up Azure DevOps Variable Group '${VARIABLE_GROUP_NAME}'...${NC}"
GROUP_ID=$(az pipelines variable-group list \
  --group-name "$VARIABLE_GROUP_NAME" \
  --query "[0].id" -o tsv 2>/dev/null || true)

if [[ -z "$GROUP_ID" || "$GROUP_ID" == "None" ]]; then
  echo "Creating variable group '$VARIABLE_GROUP_NAME'..."
  GROUP_ID=$(az pipelines variable-group create \
    --name "$VARIABLE_GROUP_NAME" \
    --variables "PLACEHOLDER=1" \
    --query "id" -o tsv)
  echo -e "${GREEN}[OK] Variable group created (ID: $GROUP_ID).${NC}"
else
  echo -e "${YELLOW}Variable group '$VARIABLE_GROUP_NAME' already exists (ID: $GROUP_ID). Updating variables.${NC}"
fi

# ── Helper: upsert a variable (create or update) ─────────────
upsert_var() {
  local name=$1 value=$2 is_secret=${3:-false}

  # Check if variable exists
  EXISTS=$(az pipelines variable-group variable list \
    --group-id "$GROUP_ID" \
    --query "keys(@)" -o tsv 2>/dev/null | grep -w "$name" || true)

  if [[ -n "$EXISTS" ]]; then
    if [[ "$is_secret" == "true" ]]; then
      az pipelines variable-group variable update \
        --group-id "$GROUP_ID" --name "$name" \
        --value "$value" --secret true --output none
    else
      az pipelines variable-group variable update \
        --group-id "$GROUP_ID" --name "$name" \
        --value "$value" --output none
    fi
  else
    if [[ "$is_secret" == "true" ]]; then
      az pipelines variable-group variable create \
        --group-id "$GROUP_ID" --name "$name" \
        --value "$value" --secret true --output none
    else
      az pipelines variable-group variable create \
        --group-id "$GROUP_ID" --name "$name" \
        --value "$value" --output none
    fi
  fi
  echo "  ✓ $name"
}

# ── Step 6: Set all variables ─────────────────────────────────
echo -e "${CYAN}[6/6] Writing all variables to Azure DevOps...${NC}"

# OCI Auth
upsert_var "TF_VAR_tenancy_ocid"        "$OCI_TENANCY"
upsert_var "TF_VAR_user_ocid"           "$OCI_USER"
upsert_var "TF_VAR_fingerprint"         "$TF_FINGERPRINT"
upsert_var "TF_VAR_region"              "$OCI_REGION"
upsert_var "TF_VAR_compartment_id"      "$OCI_TENANCY"  # root compartment
upsert_var "TF_VAR_availability_domain" "$OCI_AD"

# SSH key for VM login
SSH_PUB_KEY=$(cat "$HOME/.ssh/codexrelic_ed25519.pub" 2>/dev/null \
  || (ssh-keygen -t ed25519 -f "$HOME/.ssh/codexrelic_ed25519" -N "" -C "codexrelic-admin" -q && cat "$HOME/.ssh/codexrelic_ed25519.pub"))
upsert_var "TF_VAR_ssh_public_key"      "$SSH_PUB_KEY"

# OCI API key (base64 encoded, secret)
upsert_var "OCI_PRIVATE_KEY_B64"        "$TF_KEY_B64"   "true"

# OCI S3 State backend (secrets)
upsert_var "TF_STATE_BUCKET"            "$TF_STATE_BUCKET"
upsert_var "TF_STATE_ENDPOINT"          "$TF_STATE_ENDPOINT"
upsert_var "TF_STATE_ACCESS_KEY"        "$TF_STATE_ACCESS_KEY"
upsert_var "TF_STATE_SECRET_KEY"        "$TF_STATE_SECRET_KEY" "true"

# Remove placeholder if it was newly created
az pipelines variable-group variable delete \
  --group-id "$GROUP_ID" --name "PLACEHOLDER" --yes --output none 2>/dev/null || true

echo ""
echo -e "${GREEN}${BOLD}"
echo "============================================================"
echo "  All done! Azure DevOps Variable Group is ready.          "
echo "============================================================"
echo -e "${NC}"
echo -e "${YELLOW}Variables configured in group '${VARIABLE_GROUP_NAME}':${NC}"
echo ""
echo -e "  ${BOLD}OCI Authentication${NC}"
echo "  TF_VAR_tenancy_ocid        = $OCI_TENANCY"
echo "  TF_VAR_user_ocid           = $OCI_USER"
echo "  TF_VAR_fingerprint         = $TF_FINGERPRINT"
echo "  TF_VAR_region              = $OCI_REGION"
echo "  TF_VAR_compartment_id      = $OCI_TENANCY"
echo "  TF_VAR_availability_domain = $OCI_AD"
echo "  TF_VAR_ssh_public_key      = (your ed25519 pub key)"
echo "  OCI_PRIVATE_KEY_B64        = (secret - base64 RSA key)"
echo ""
echo -e "  ${BOLD}OCI S3 State Backend${NC}"
echo "  TF_STATE_BUCKET            = $TF_STATE_BUCKET"
echo "  TF_STATE_ENDPOINT          = $TF_STATE_ENDPOINT"
echo "  TF_STATE_ACCESS_KEY        = $TF_STATE_ACCESS_KEY"
echo "  TF_STATE_SECRET_KEY        = (secret)"
echo ""
echo -e "${CYAN}You can now trigger the pipeline in Azure DevOps!${NC}"
