import re
import os

files = [
    'old/old.md',
    'docs/kubernetes-v2.0-architecture.md',
    'docs/LEARNINGS_AND_ISSUES.md'
]

for fp in files:
    if not os.path.exists(fp):
        continue
    with open(fp, 'r') as f:
        c = f.read()
    
    # Remove lines containing ArgoCD/Argo CD/Argo Rollout
    new_lines = []
    for line in c.split('\n'):
        if 'argo' in line.lower() or 'argocd' in line.lower():
            continue
        new_lines.append(line)
        
    c = '\n'.join(new_lines)
    
    with open(fp, 'w') as f:
        f.write(c)

