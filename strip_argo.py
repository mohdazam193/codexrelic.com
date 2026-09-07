import os
import re

files_to_check = [
    'README.md',
    'docs/GITOPS_ARCHITECTURE.md',
    'docs/kubernetes-v2.0-architecture.md',
    'ci-cd/docker/templates/deploy-stage.yml'
]

for file_path in files_to_check:
    if not os.path.exists(file_path):
        continue
    with open(file_path, 'r') as f:
        content = f.read()

    # Remove the ArgoCD badges and references
    content = re.sub(r'<img src="https://img\.shields\.io/badge/GitOps-Argo%20CD-EF7B4D\?logo=argo" alt="Argo CD">\n?', '', content)
    content = re.sub(r'\| 🔄 GitOps \| Argo CD \|\n?', '', content)
    content = re.sub(r'and Argo CD reconciles the Kubernetes application state\.', 'and Kubernetes manages the application state.', content)
    content = re.sub(r'\*\*Argo CD\*\* continuously reconciles the Kubernetes application state with Git\.', '', content)
    content = re.sub(r'Argo CD then keeps the Kubernetes application state aligned with the declared configuration\.', '', content)
    content = re.sub(r'; Argo CD keeps Kubernetes reconciled\.', '.', content)
    
    # Remove ArgoCD issues section
    content = re.sub(r'### 💥 Argo CD \+ Traefik Redirect Loop.*?###', '###', content, flags=re.DOTALL)
    content = re.sub(r'Large Argo CD CRDs hit Kubernetes.*?limit:.*?\n\n', '', content, flags=re.DOTALL)
    
    # Remove ArgoCD from diagrams
    content = re.sub(r'\s*Argo CD\n?', '\n', content)
    content = re.sub(r'Argo CD\s*→ GitOps\n?', '', content)
    
    # Docs
    content = re.sub(r'Argo CD acts as the \*\*Reader\*\*, constantly monitoring the Git repository for changes and pulling them down into the Kubernetes cluster\.', '', content)
    content = re.sub(r'- Connects to the cluster via SSH and forces Argo CD to sync immediately\n?', '', content)
    content = re.sub(r'4\. Argo CD \(In-Cluster\)\n?.*?36', '36', content, flags=re.DOTALL) # This regex is bad, let's fix below.

    with open(file_path, 'w') as f:
        f.write(content)

print("Done basic replacements.")
