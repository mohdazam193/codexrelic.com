#!/usr/bin/env bash
# ============================================================
# 02-keyvault/create-and-populate-keyvaults.sh
# Automates: Implementation Plan Parts 2–3
#
# What this does:
#   - Creates resource group rg-codexrelic (if not exists) Modify as per your choice when needed
#   - Creates 3 Azure Key Vaults (UAT, Stage, Prod)
#   - Grants the Azure DevOps service principal Get+List on secrets
#   - Populates all 5 secrets into each vault
#     (reads from keys/ files if present, else prompts interactively)
#
# Prerequisites:
#   - Azure CLI installed and logged in (az login)
#   - run generate-keys.sh first (or have values ready to paste)
#
# Usage:
#   bash automation/02-keyvault/create-and-populate-keyvaults.sh
# ============================================================

set -euo pipefail

# ── Colours ──
RED='\033[0;31m'; YELLOW='\033[1;33m'; GREEN='\033[0;32m'; CYAN='\033[0;36m'; NC='\033[0m'

echo ""
echo -e "${CYAN}============================================================${NC}"
echo -e "${CYAN}  codexrelic.com — Azure Key Vault Setup                   ${NC}"
echo -e "${CYAN}============================================================${NC}"
echo ""

# ── Check az CLI ──
if ! command -v az &>/dev/null; then
  echo -e "${RED}[ERROR] Azure CLI not found.${NC}"
  echo "  Install: https://docs.microsoft.com/cli/azure/install-azure-cli"
  exit 1
fi

# ── Check logged in ──
az account show &>/dev/null || {
  echo -e "${YELLOW}[INFO] Not logged in. Running az login...${NC}"
  az login
}

# ── Config ──
RESOURCE_GROUP="rg-codexrelic"
LOCATION="eastus"             # Change if you prefer a different region
KEYS_DIR="$(dirname "$0")/../../keys"

VAULTS=(
  "kv-uat-codexrelic:uat"
  "kv-stage-codexrelic:stage"
  "kv-prod-codexrelic:prod"
)

# ── Helper: read from file or prompt ──
read_secret() {
  local FILE="$1"
  local PROMPT="$2"
  if [[ -f "$FILE" ]]; then
    cat "$FILE" | tr -d '\n'
  else
    echo -en "${YELLOW}  ${PROMPT}: ${NC}" >&2
    read -r VALUE
    echo "$VALUE"
  fi
}

# ── Step 1: Resource Group ──
echo -e "${CYAN}[1/4] Ensuring resource group '${RESOURCE_GROUP}' exists...${NC}"
az group create \
  --name "$RESOURCE_GROUP" \
  --location "$LOCATION" \
  --output none
echo -e "${GREEN}  ✓ Resource group ready${NC}"
echo ""

# ── Get DevOps service principal object ID ──
echo -e "${YELLOW}Enter the Object ID of your Azure DevOps service principal.${NC}"
echo -e "${YELLOW}Find it: Azure Portal → Entra ID → App registrations → your SP → Object ID${NC}"
echo -e "${YELLOW}(Leave blank to skip access policy — you can add it manually later)${NC}"
echo -en "Service Principal Object ID: "
read -r SP_OBJECT_ID

# ── Step 2: Create Vaults + Grant Access ──
echo ""
echo -e "${CYAN}[2/4] Creating Key Vaults...${NC}"

for ENTRY in "${VAULTS[@]}"; do
  VAULT_NAME="${ENTRY%%:*}"
  ENV="${ENTRY##*:}"

  echo -e "  Creating ${YELLOW}${VAULT_NAME}${NC}..."

  az keyvault create \
    --name "$VAULT_NAME" \
    --resource-group "$RESOURCE_GROUP" \
    --location "$LOCATION" \
    --sku standard \
    --enabled-for-deployment false \
    --output none 2>/dev/null && \
    echo -e "  ${GREEN}✓ Created${NC}" || \
    echo -e "  ${YELLOW}⚠ Already exists — skipping create${NC}"

  # Grant DevOps SP access if Object ID was provided
  if [[ -n "$SP_OBJECT_ID" ]]; then
    az keyvault set-policy \
      --name "$VAULT_NAME" \
      --object-id "$SP_OBJECT_ID" \
      --secret-permissions get list \
      --output none
    echo -e "  ${GREEN}✓ Access policy set for service principal${NC}"
  fi
done

echo ""
echo -e "${CYAN}[3/4] Collecting secrets for each environment...${NC}"
echo -e "${YELLOW}(Values will be read from keys/ directory if generate-keys.sh was run first)${NC}"
echo ""

# ── Step 3: Populate Secrets ──
for ENTRY in "${VAULTS[@]}"; do
  VAULT_NAME="${ENTRY%%:*}"
  ENV="${ENTRY##*:}"

  echo -e "${CYAN}── ${VAULT_NAME} (${ENV}) ──${NC}"

  # MongoDB URI
  echo -en "${YELLOW}  MONGO_URI for ${ENV} (e.g. mongodb+srv://user:pass@cluster.mongodb.net/codexrelic_${ENV}): ${NC}"
  read -r MONGO_URI

  # JWT secret
  JWT_SECRET=$(read_secret "${KEYS_DIR}/${ENV}-jwt-secret.txt" "JWT_SECRET (64-char hex)")

  echo -e "  Setting secrets in ${YELLOW}${VAULT_NAME}${NC}..."

  az keyvault secret set --vault-name "$VAULT_NAME" --name "MONGO-URI"                 --value "$MONGO_URI"   --output none
  az keyvault secret set --vault-name "$VAULT_NAME" --name "JWT-SECRET"                  --value "$JWT_SECRET"  --output none

  echo -e "  ${GREEN}✓ 2 secrets set in ${VAULT_NAME}${NC}"
  echo ""
done

# ── Step 4: Verify ──
echo -e "${CYAN}[4/4] Verifying secrets in each vault...${NC}"

for ENTRY in "${VAULTS[@]}"; do
  VAULT_NAME="${ENTRY%%:*}"
  echo -e "  ${YELLOW}${VAULT_NAME}:${NC}"
  az keyvault secret list \
    --vault-name "$VAULT_NAME" \
    --query "[].name" \
    --output table 2>/dev/null | grep -v "^Name\|^----" | sed 's/^/    /'
done

echo ""
echo -e "${CYAN}============================================================${NC}"
echo -e "${GREEN}[DONE] All 3 Key Vaults created and populated.${NC}"
echo ""
echo -e "  Next steps:"
echo -e "  ${YELLOW}1.${NC} Verify secrets in Azure Portal → Key Vaults"
echo -e "  ${YELLOW}2.${NC} Update azure-pipelines.yml with AzureKeyVault@2 task"
echo -e "  ${YELLOW}3.${NC} Provision OCI ARM VM"
echo -e "${CYAN}============================================================${NC}"
echo ""
