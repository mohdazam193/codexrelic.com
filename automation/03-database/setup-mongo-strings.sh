#!/usr/bin/env bash
# ============================================================
# 03-database/setup-mongo-strings.sh
# Automates: Formatting and pushing MongoDB connection strings
#
# What this does:
#   - Asks for your raw MongoDB Atlas connection string and password
#   - Automatically formats it for UAT, Stage, and Prod databases
#   - Pushes the MONGO-URI secret directly into your 3 Azure Key Vaults
#
# Prerequisites:
#   - Azure CLI installed and logged in (az login)
#   - The 3 Key Vaults must already exist (run 02-keyvault first)
#
# Usage:
#   bash automation/03-database/setup-mongo-strings.sh
# ============================================================

set -euo pipefail

# ── Colours ──
RED='\033[0;31m'; YELLOW='\033[1;33m'; GREEN='\033[0;32m'; CYAN='\033[0;36m'; NC='\033[0m'

echo ""
echo -e "${CYAN}============================================================${NC}"
echo -e "${CYAN}  codexrelic.com — MongoDB Connection String Automation    ${NC}"
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

echo -e "${CYAN}[1/3] Collect Base MongoDB Details${NC}"
echo -e "${YELLOW}Go to MongoDB Atlas -> Connect -> Drivers -> Python${NC}"
echo -e "${YELLOW}Copy the connection string. It should look like:${NC}"
echo -e "mongodb+srv://codexrelic_db_admin:<password>@cluster0.abcde.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
echo ""

echo -en "${YELLOW}Paste the raw connection string: ${NC}"
read -r RAW_URI

echo -en "${YELLOW}Enter the database password (replaces <password>): ${NC}"
read -rs DB_PASS
echo ""

# Validate the string format
if [[ "$RAW_URI" != *"mongodb+srv://"* ]]; then
  echo -e "${RED}[ERROR] Invalid connection string format.${NC}"
  exit 1
fi

# ── Format the strings ──
echo ""
echo -e "${CYAN}[2/3] Formatting Connection Strings...${NC}"

# Extract base up to the slash before parameters
BASE_URI=$(echo "$RAW_URI" | sed -E 's/\/\?.*//')
PARAMS="?retryWrites=true&w=majority"

# Replace <password> with actual password (URL encoding might be needed if password has special chars, but we assume alphanumeric/safe for now)
BASE_URI_WITH_PASS="${BASE_URI/<password>/$DB_PASS}"

URI_UAT="${BASE_URI_WITH_PASS}/codexrelic_uat${PARAMS}"
URI_STAGE="${BASE_URI_WITH_PASS}/codexrelic_stage${PARAMS}"
URI_PROD="${BASE_URI_WITH_PASS}/codexrelic_prod${PARAMS}"

echo -e "  ${GREEN}✓ Generated UAT URI${NC}"
echo -e "  ${GREEN}✓ Generated Stage URI${NC}"
echo -e "  ${GREEN}✓ Generated Prod URI${NC}"

# ── Push to Key Vaults ──
echo ""
echo -e "${CYAN}[3/3] Pushing to Azure Key Vaults...${NC}"

echo -e "  Pushing to ${YELLOW}kv-uat-codexrelic${NC}..."
az keyvault secret set --vault-name "kv-uat-codexrelic" --name "MONGO-URI" --value "$URI_UAT" --output none

echo -e "  Pushing to ${YELLOW}kv-stage-codexrelic${NC}..."
az keyvault secret set --vault-name "kv-stage-codexrelic" --name "MONGO-URI" --value "$URI_STAGE" --output none

echo -e "  Pushing to ${YELLOW}kv-prod-codexrelic${NC}..."
az keyvault secret set --vault-name "kv-prod-codexrelic" --name "MONGO-URI" --value "$URI_PROD" --output none

echo ""
echo -e "${CYAN}============================================================${NC}"
echo -e "${GREEN}[DONE] Database connection strings formatted and securely stored!${NC}"
echo -e "${CYAN}============================================================${NC}"
