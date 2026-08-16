#!/usr/bin/env bash
# ============================================================
# 01-auth-setup/generate-keys.sh
# Automates: AUTH_SETUP.md Steps 1–3
#
# What this does:
#   - Generates one Ed25519 keypair per environment (UAT, Stage, Prod)
#   - Generates one JWT secret per environment (256-bit hex)
#   - Prints all values clearly to terminal
#   - Saves private keys + JWT secrets to a local keys/ directory
#     (gitignored — never committed)
#
# Usage:
#   bash automation/01-auth-setup/generate-keys.sh
# ============================================================

set -euo pipefail

# ── Colours ──
RED='\033[0;31m'; YELLOW='\033[1;33m'; GREEN='\033[0;32m'; CYAN='\033[0;36m'; NC='\033[0m'

echo ""
echo -e "${CYAN}============================================================${NC}"
echo -e "${CYAN}  codexrelic.com — Auth Key Generation                     ${NC}"
echo -e "${CYAN}============================================================${NC}"
echo ""

# ── Check Python 3 + cryptography ──
if ! command -v python3 &>/dev/null; then
  echo -e "${RED}[ERROR] python3 not found. Install it and try again.${NC}"
  exit 1
fi

python3 -c "from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey" 2>/dev/null || {
  echo -e "${YELLOW}[INFO] Installing cryptography package...${NC}"
  pip3 install cryptography --quiet
}

# ── Output directory ──
KEYS_DIR="$(dirname "$0")/../../keys"
mkdir -p "$KEYS_DIR"

# ── Warn if keys/ is not gitignored ──
GITIGNORE="$(dirname "$0")/../../.gitignore"
if ! grep -q "^keys/" "$GITIGNORE" 2>/dev/null; then
  echo "keys/" >> "$GITIGNORE"
  echo -e "${YELLOW}[INFO] Added keys/ to .gitignore${NC}"
fi

# ── Generate keys for each environment ──
ENVS=("uat" "stage" "prod")

for ENV in "${ENVS[@]}"; do
  echo -e "${CYAN}── Generating keypair for: ${ENV} ──${NC}"

  OUTPUT=$(python3 - <<'PYEOF'
import sys, base64
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.serialization import Encoding, PrivateFormat, PublicFormat, NoEncryption
import secrets

key = Ed25519PrivateKey.generate()
priv = key.private_bytes(Encoding.Raw, PrivateFormat.Raw, NoEncryption())
pub  = key.public_key().public_bytes(Encoding.Raw, PublicFormat.Raw)
jwt  = secrets.token_hex(32)

print(base64.b64encode(priv).decode())
print(base64.b64encode(pub).decode())
print(jwt)
PYEOF
)

  PRIV_KEY=$(echo "$OUTPUT" | sed -n '1p')
  PUB_KEY=$(echo  "$OUTPUT" | sed -n '2p')
  JWT_SEC=$(echo  "$OUTPUT" | sed -n '3p')

  # Save to files
  echo "$PRIV_KEY" > "$KEYS_DIR/${ENV}-private-key.txt"
  echo "$PUB_KEY"  > "$KEYS_DIR/${ENV}-public-key.txt"
  echo "$JWT_SEC"  > "$KEYS_DIR/${ENV}-jwt-secret.txt"
  chmod 600 "$KEYS_DIR/${ENV}-private-key.txt" "$KEYS_DIR/${ENV}-jwt-secret.txt"

  echo -e "  ${GREEN}PRIVATE KEY${NC} (keep safe — never share):"
  echo -e "  ${PRIV_KEY}"
  echo ""
  echo -e "  ${GREEN}PUBLIC KEY${NC} (goes in .env.${ENV} as ADMIN_ED25519_PUBLIC_KEY):"
  echo -e "  ${PUB_KEY}"
  echo ""
  echo -e "  ${GREEN}JWT SECRET${NC} (goes in .env.${ENV} as JWT_SECRET):"
  echo -e "  ${JWT_SEC}"
  echo ""
  echo -e "  ${YELLOW}Saved to: keys/${ENV}-{private-key,public-key,jwt-secret}.txt${NC}"
  echo ""
done

echo -e "${CYAN}============================================================${NC}"
echo -e "${GREEN}[DONE] All keypairs and JWT secrets generated.${NC}"
echo ""
echo -e "  Files saved in: ${YELLOW}keys/${NC}"
echo -e "  ${RED}⚠  keys/ is gitignored. Back up private keys to a password manager.${NC}"
echo -e "${CYAN}============================================================${NC}"
echo ""
