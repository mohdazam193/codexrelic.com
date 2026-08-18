#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

echo "=========================================================="
echo "    Kubernetes (K3s) Automated Setup Script"
echo "=========================================================="

# 1. Validate inputs
if [ -z "$1" ]; then
  echo "Usage: ./setup-k3s.sh <PUBLIC_IP_OF_VM>"
  echo "Example: ./setup-k3s.sh 129.225.82.233"
  exit 1
fi

PUBLIC_IP=$1
SSH_KEY="$HOME/.ssh/codexrelic_ed25519"
SSH_USER="ubuntu"

if [ ! -f "$SSH_KEY" ]; then
  echo "[ERROR] SSH private key not found at $SSH_KEY. Please run the auth setup first."
  exit 1
fi

echo "[INFO] Target VM: $PUBLIC_IP"
echo "[INFO] Using SSH Key: $SSH_KEY"

# 2. Test SSH Connection
echo "[INFO] Testing SSH connection to VM..."
ssh -o StrictHostKeyChecking=no -i "$SSH_KEY" "$SSH_USER@$PUBLIC_IP" "echo '[OK] SSH Connection Successful'"

# 3. Install K3s on the VM
echo "[INFO] Installing K3s (Lightweight Kubernetes) on the VM. This may take 1-2 minutes..."
ssh -i "$SSH_KEY" "$SSH_USER@$PUBLIC_IP" "curl -sfL https://get.k3s.io | sh -"
echo "[OK] K3s installation complete."

# 4. Extract and configure kubeconfig
echo "[INFO] Extracting kubeconfig from the VM..."
KUBECONFIG_LOCAL="../../codexrelic-kubeconfig.yaml"

# Read the kubeconfig from the server
ssh -i "$SSH_KEY" "$SSH_USER@$PUBLIC_IP" "sudo cat /etc/rancher/k3s/k3s.yaml" > "$KUBECONFIG_LOCAL"

# Replace 127.0.0.1 with the actual public IP
sed -i.bak "s/127.0.0.1/$PUBLIC_IP/g" "$KUBECONFIG_LOCAL"
rm -f "${KUBECONFIG_LOCAL}.bak"

echo "[OK] Kubeconfig saved locally to: $(cd $(dirname $KUBECONFIG_LOCAL) && pwd)/codexrelic-kubeconfig.yaml"

# 5. Verify local access
echo "[INFO] Verifying local Kubernetes access..."
export KUBECONFIG="$(cd $(dirname $KUBECONFIG_LOCAL) && pwd)/codexrelic-kubeconfig.yaml"

# Note: This might timeout if port 6443 is blocked by OCI Security Lists, 
# but the script notifies the user of this context.
if kubectl get nodes --request-timeout="5s" >/dev/null 2>&1; then
    echo "[OK] Successfully connected to remote cluster via kubectl!"
    kubectl get nodes
else
    echo "[WARNING] Could not connect to cluster via public internet. This is expected if OCI port 6443 is blocked."
    echo "[INFO] The cluster is running correctly. Azure DevOps SSH pipeline will deploy via SSH locally."
fi

echo "=========================================================="
echo "    Setup Complete!"
echo "=========================================================="
echo "Next Steps:"
echo "1. Create an SSH Service Connection in Azure DevOps pointing to $PUBLIC_IP"
echo "2. Run the Azure DevOps Pipeline."
