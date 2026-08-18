# Kubernetes (K3s) Setup Guide

This document outlines the entire process of how we transformed a bare Ubuntu Virtual Machine into a functioning Kubernetes node, and how the Azure DevOps pipeline was configured to deploy to it securely.

## 1. Why K3s?
We chose **K3s** (a lightweight Kubernetes distribution by Rancher) over full Kubernetes or standard Docker for several reasons:
- **Efficiency:** It ships as a single binary and uses less than 500 MB of RAM, making it perfect for our 2 OCPU / 12 GB RAM ARM instance.
- **Features:** It provides all the enterprise features of Kubernetes (zero-downtime rolling updates, self-healing, scaling) without the overhead of `etcd` or complex control planes.
- **Built-in Ingress:** It comes pre-packaged with Traefik for easy HTTP/HTTPS routing.

## 2. Server Installation
The installation was performed directly on the newly provisioned OCI VM over SSH. 

The exact command run on the VM was:
```bash
curl -sfL https://get.k3s.io | sh -
```

This single command:
1. Downloads the K3s ARM64 binary.
2. Configures a `systemd` service (`k3s.service`).
3. Starts a combined Kubernetes Control Plane and Worker Node.
4. Generates a `kubeconfig` file at `/etc/rancher/k3s/k3s.yaml`.

## 3. Remote Access Configuration
By default, the `kubeconfig` on the VM points to `127.0.0.1` (localhost). To access the cluster remotely (e.g., from your local laptop):
1. We fetched the config via SSH:
   `ssh -i ~/.ssh/codexrelic_ed25519 ubuntu@129.225.82.233 "sudo cat /etc/rancher/k3s/k3s.yaml"`
2. We replaced `127.0.0.1` with the VM's public IP `129.225.82.233`.
3. We saved this file locally as `codexrelic-kubeconfig.yaml` and added it to `.gitignore` to prevent leaking the cluster certificates.

## 4. Azure DevOps Integration Strategy
A standard Kubernetes deployment in Azure DevOps uses the `Kubernetes@1` task, which requires exposing the Kubernetes API (port 6443) to the public internet so Microsoft's build agents can connect to it.

**We rejected this approach for security.** Oracle Cloud's security lists block port 6443 by default, and opening it to the entire internet is a risk.

### The SSH Pipeline Solution
Instead of exposing the cluster, we updated the pipeline (`ci-cd/docker/azure-pipelines.yml`) to use **SSH deployments**. 

The pipeline performs the following steps:
1. **CopyFilesOverSSH:** Securely SCPs the Kubernetes manifests (`deployment.yaml`, `service.yaml`) and the rendered `.env` file directly to the `/home/ubuntu/` directory on the VM.
2. **SSH:** Logs into the VM via SSH and runs `kubectl` commands locally.
   - It creates isolated namespaces (`uat`, `stage`, `prod`).
   - It injects the `.env` file securely into a Kubernetes Secret.
   - It applies the manifests to spin up the Docker containers.

Because the pipeline uses SSH, port 22 is the *only* management port that needs to be open on the server firewall.

## 5. Kubernetes Manifests
We created two core files in the `kubernetes/` folder to manage the application:
- **`deployment.yaml`:** Tells Kubernetes to run 2 replicas of the application, injecting the Key Vault secrets via `envFrom`. It acts as the source of truth for the desired state.
- **`service.yaml`:** Exposes the application containers internally and binds them to a NodePort (30080) so external traffic hitting the VM can be routed to the pods.
