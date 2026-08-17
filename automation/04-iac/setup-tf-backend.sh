#!/usr/bin/env bash
# ============================================================
# 04-iac/setup-tf-backend.sh
# Automates: Creating Azure Storage Account for Terraform State
#
# What this does:
#   - Creates a new Azure Resource Group for Terraform state
#   - Creates an Azure Storage Account and Blob Container
#   - Outputs the exact variables you need to add to your Azure DevOps pipeline
#
# Usage:
#   bash automation/04-iac/setup-tf-backend.sh
# ============================================================

set -euo pipefail

RED='\033[0;31m'; YELLOW='\033[1;33m'; GREEN='\033[0;32m'; CYAN='\033[0;36m'; NC='\033[0m'

echo -e "${CYAN}============================================================${NC}"
echo -e "${CYAN}  codexrelic.com — Terraform State Backend Setup           ${NC}"
echo -e "${CYAN}============================================================${NC}"

if ! command -v az &>/dev/null; then
  echo -e "${RED}[ERROR] Azure CLI not found.${NC}"
  exit 1
fi

az account show &>/dev/null || az login

# Configuration
RG_NAME="rg-terraform-state"
LOCATION="eastus"
# Storage account names must be globally unique, lowercase, 3-24 chars
export LC_ALL=C
RAND=$(head -c 100 /dev/urandom | tr -dc 'a-z0-9' | head -c 6)
SA_NAME="tfstatecodexrelic${RAND}"
CONTAINER_NAME="tfstate"

echo -e "\n${CYAN}[1/3] Creating Resource Group: ${RG_NAME}...${NC}"
az group create --name "$RG_NAME" --location "$LOCATION" --output none

echo -e "${CYAN}[2/3] Creating Storage Account: ${SA_NAME}...${NC}"
az storage account create \
  --name "$SA_NAME" \
  --resource-group "$RG_NAME" \
  --location "$LOCATION" \
  --sku Standard_LRS \
  --encryption-services blob \
  --output none

echo -e "${CYAN}[3/3] Creating Blob Container: ${CONTAINER_NAME}...${NC}"
# Get storage account key to create container
ACCOUNT_KEY=$(az storage account keys list --resource-group "$RG_NAME" --account-name "$SA_NAME" --query '[0].value' -o tsv)

az storage container create \
  --name "$CONTAINER_NAME" \
  --account-name "$SA_NAME" \
  --account-key "$ACCOUNT_KEY" \
  --output none

echo -e "\n${GREEN}[DONE] Terraform Azure Backend Successfully Created!${NC}"
echo -e "${YELLOW}Add the following variables to your 'terraform' Variable Group in Azure DevOps:${NC}"
echo -e "------------------------------------------------------------"
echo -e "TF_STATE_RG        = ${RG_NAME}"
echo -e "TF_STATE_SA        = ${SA_NAME}"
echo -e "TF_STATE_CONTAINER = ${CONTAINER_NAME}"
echo -e "------------------------------------------------------------"
