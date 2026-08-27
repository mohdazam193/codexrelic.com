# Argo CD Centralized Deployment

This directory contains the Kubernetes manifests required to deploy and configure a centralized Argo CD instance that manages the UAT, Stage, and Prod environments.

## Deployment Steps

To install Argo CD using these configurations via Azure Pipelines (or manually), follow these steps:

### 1. Create Namespace
First, ensure the `argocd` namespace exists:
```bash
kubectl create namespace argocd || true
```

### 2. Apply Argo CD Core and Ingress
Apply the kustomization in this directory. This pulls the official Argo CD manifests and configures the Ingress for `argo.codexrelic.com`.
```bash
kubectl apply -k ci-cd/argo/
```

### 3. Inject KeyVault Password (Azure Pipelines)
Argo CD's default admin username is `admin`. To use your existing `O2-ROOT-PASSWORD` from Azure Key Vault, your pipeline must hash it using `bcrypt` and patch the Argo CD secret.

Add this bash step to your Azure DevOps pipeline *after* pulling secrets from Key Vault:
```bash
# Hash the KeyVault password using bcrypt (requires apache2-utils/htpasswd installed on the runner)
HASHED_PASSWORD=$(htpasswd -bnBC 10 "" $O2_ROOT_PASSWORD | tr -d ':\n')

# Patch the Argo CD secret
kubectl -n argocd patch secret argocd-secret \
  -p '{"stringData": {
    "admin.password": "'$HASHED_PASSWORD'",
    "admin.passwordMtime": "'$(date +%FT%T%Z)'"
  }}'
```

### 4. Configure Private Repository Access
Because your repository is private, Argo CD needs a token (like a GitHub Personal Access Token) to read your manifests. Your Azure Pipeline can create this secret using another secret from your Key Vault (e.g., `GIT_PAT`):
```bash
kubectl create secret generic codexrelic-repo-secret \
  -n argocd \
  --from-literal=url=https://github.com/mohdazam193/codexrelic.com.git \
  --from-literal=password=$GIT_PAT \
  --from-literal=username=mohdazam193
kubectl label secret codexrelic-repo-secret argocd.argoproj.io/secret-type=repository -n argocd
```

### 5. Deploy Multi-Environment Applications
Finally, deploy the Argo CD `Application` manifests to instruct Argo CD to manage the `uat`, `stage`, and `prod` environments automatically based on this Git repository.
```bash
kubectl apply -f ci-cd/argo/apps/
```

## Accessing the Dashboard
Once DNS is configured for `argo.codexrelic.com`, navigate to `https://argo.codexrelic.com` and log in with username `admin` and the password from your KeyVault.
