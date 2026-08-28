# CodexRelic GitOps Architecture

This document explains the GitOps CI/CD flow powering the CodexRelic infrastructure. 

## The Core Philosophy
In a true GitOps model, **Git is the single source of truth** for both infrastructure and application configuration. This means that our deployment pipelines do *not* run imperative commands like `kubectl apply` to push changes to the cluster. 

Instead, the CI/CD pipeline acts as a **Writer**, updating the Git repository with the newly built Docker image tags. Argo CD acts as the **Reader**, constantly monitoring the Git repository for changes and pulling them down into the Kubernetes cluster.

## Architecture Flow

```text
1. Developer Pushes Code
         ↓
2. Azure DevOps Build Pipeline Triggers
   - Builds Docker Image
   - Scans with Snyk and TruffleHog
   - Pushes image to DockerHub (`aazammohammad193/codexrelic-api:<BuildID>`)
         ↓
3. Azure DevOps Release Pipeline Triggers
   - Checks out the GitHub repository using a PAT from Key Vault
   - Uses Kustomize to update the image tag for the specific environment overlay
   - Commits the new tag to `main` with the message `[skip ci]`
   - Connects to the cluster via SSH and forces Argo CD to sync immediately
         ↓
4. Argo CD (In-Cluster)
   - Detects the new commit
   - Re-evaluates the Kustomize overlays (`kubernetes/overlays/<namespace>`)
   - Reconciles the Kubernetes cluster (e.g. executing an Argo Rollout)
```

## Why We Avoid `sed` and `kubectl apply`

Previously, the Azure DevOps pipeline used `sed` to replace placeholders like `DOMAIN_PLACEHOLDER` and `DOCKER_IMAGE_PLACEHOLDER` in the raw Kubernetes manifests, and then applied them directly via SSH.

While this works for simple push-based pipelines, it **breaks** when used alongside Argo CD:
1. Argo CD is configured with `selfHeal: true`. 
2. When the pipeline runs `kubectl apply`, it temporarily fixes the cluster.
3. Three minutes later, Argo CD wakes up, looks at the Git repository, sees the raw `DOMAIN_PLACEHOLDER` text, and realizes the cluster has "drifted".
4. Argo CD immediately overwrites the pipeline's changes with the broken YAML from Git, causing the pods to fail with `ImagePullBackOff` and ingress errors.

By updating the pipeline to commit the new image tag back to Git, we ensure that Argo CD and the Pipeline are working together instead of fighting each other.

## Kustomize Structure

We use **Kustomize** to cleanly manage configuration differences between environments without resorting to string replacement scripts.

The manifests are structured as follows:
- `kubernetes/base/`: Contains the common manifests (Rollout, Service, HPA) used by all environments.
- `kubernetes/overlays/uat/`: Patches the UAT specific Ingress domain and replica count.
- `kubernetes/overlays/stage/`: Patches the Stage specific Ingress domain and replica count.
- `kubernetes/overlays/prod/`: Patches the Prod specific Ingress domain and replica count.

Argo CD's Application definitions (in `ci-cd/argo/apps/`) point directly to these overlay directories.

## Resolving Infinite CI Loops
When the Release Pipeline commits the new image tag to the `main` branch, it normally would trigger the Build Pipeline again, resulting in an infinite loop. We bypass this by appending `[skip ci]` to the Git commit message. Azure DevOps automatically recognizes this tag and skips triggering subsequent builds for that specific commit.
