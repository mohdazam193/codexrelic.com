# Kubernetes (K3s) Step-by-Step Setup Guide

This guide provides exact, step-by-step instructions for provisioning and deploying the Kubernetes cluster to the OCI Virtual Machine. It is designed so that any new developer can replicate the entire setup from scratch.

## Prerequisites
1. You have successfully run the Terraform pipeline and your OCI VM is running.
2. You have the **Public IP Address** of your VM (e.g., `129.225.82.233`).
3. You have the `codexrelic_ed25519` private SSH key in your `~/.ssh/` directory.

---

## Step 1: Install Kubernetes (K3s) on the VM

We use **K3s** (a lightweight Kubernetes distribution by Rancher) because it runs perfectly on the Free Tier ARM instance without consuming too much memory.

To automate this, we have provided a bash script that SSHs into your VM, installs K3s, and extracts the connection configuration for you.

Run the automation script from the root of the repository, passing your VM's public IP:

```bash
cd codexrelic.com
./automation/05-kubernetes/setup-k3s.sh <PUBLIC_IP>
```

**What this script does:**
1. Tests SSH connectivity.
2. Runs the K3s installation command (`curl -sfL https://get.k3s.io | sh -`).
3. Downloads the cluster `kubeconfig` file from the VM.
4. Modifies the config to point to the public IP instead of localhost.
5. Saves it locally as `codexrelic-kubeconfig.yaml` (this file is `.gitignore`d for security).

---

## Step 2: Configure Azure DevOps SSH Service Connection

We intentionally **do not** open the Kubernetes API port (6443) to the public internet because OCI firewalls block it by default, and opening it is a security risk.

Instead, Azure DevOps will deploy our application by securely SSHing into the VM and running `kubectl apply` locally. You must grant Azure DevOps this SSH access.

1. Go to your Azure DevOps Project.
2. Click **Project Settings** (bottom left corner) -> **Service Connections**.
3. Click **New service connection** -> Select **SSH**.
4. Fill out the form exactly as follows:
   - **Host name:** `<YOUR_VM_PUBLIC_IP>` (e.g., `129.225.82.233`)
   - **User name:** `ubuntu`
   - **Private key:** *(Paste the entire contents of your `codexrelic_ed25519` private key here)*
   - **Service connection name:** `oci-vm-ssh` *(Warning: This must be exact, as it is hardcoded in the pipeline!)*
5. Click **Verify and Save**.

---

## Step 3: Configure Kubernetes Namespaces & Secrets (Manual or Automated)

If you are deploying manually via the terminal, you must create an isolated namespace for your environment (e.g., `uat`, `stage`, `prod`) and securely load your `.env` variables into Kubernetes as a Secret.

**1. Create a Namespace:**
```bash
kubectl create namespace uat
```

**2. Create the Secret:**
Assuming you have a `.env` file locally containing your database URI and JWT secrets:
```bash
kubectl create secret generic codexrelic-secrets \
  --namespace=uat \
  --from-env-file=.env
```

*(Note: If you use the Azure DevOps pipeline in Step 5, it will run these commands automatically for you by pulling the secrets directly from Azure Key Vault.)*

---

## Step 4: Understand the Kubernetes Manifests

Before deploying, review the two files we added to the `kubernetes/` folder:

1. **`deployment.yaml`**: This tells Kubernetes to run 2 replicas of your Docker container. It pulls the image built by Azure DevOps and injects the `codexrelic-secrets` into the container as environment variables.
2. **`service.yaml`**: This maps the internal container port (3000) to an external NodePort (`30080`), allowing traffic to reach your application.

To apply these manifests manually:
```bash
kubectl apply -n uat -f kubernetes/deployment.yaml
kubectl apply -n uat -f kubernetes/service.yaml
```

---

## Step 5: Run the Application CI/CD Pipeline

With the VM configured and the SSH Service Connection saved, you are ready to deploy!

1. Go to Azure DevOps -> **Pipelines**.
2. Run the Docker CI/CD pipeline (`ci-cd/docker/azure-pipelines.yml`).

**How the Pipeline Works:**
- **Build Stage:** Builds the Docker image and pushes it to DockerHub.
- **Deploy Stages (UAT, Stage, Prod):**
  1. Pulls environment secrets from Azure Key Vault.
  2. Uses `CopyFilesOverSSH` to push the Kubernetes manifests and the `.env` file to the VM.
  3. Uses `SSH` to log into the VM and execute `kubectl`:
     - Creates the required namespace (e.g., `uat`).
     - Converts the `.env` file into a secure Kubernetes Secret.
     - Injects the new Docker Image Tag into `deployment.yaml`.
     - Applies the manifests (`kubectl apply`).
     - Waits for the pods to roll out successfully.

---

## Step 6: Map your DNS (Final Step)

Once the pipeline succeeds, your application is running inside Kubernetes on the VM! The final step is to point your public domain name (`codexrelic.com`) to the VM.

Please follow the instructions in the [**DNS_SETUP.md**](./DNS_SETUP.md) file to configure your DNS records and prepare the server for HTTPS.
