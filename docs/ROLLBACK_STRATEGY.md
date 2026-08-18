# Rollback Strategy

Because we decoupled the Build and Release pipelines, rolling back to an older version of your application is incredibly simple and reliable. There are two ways to perform a rollback:

## Method 1: Pipeline Rollback (Recommended)

If a bad deployment makes it to Production and you need to revert it, you don't need to rebuild old code! 

Because the Release pipeline pulls immutable artifacts and image tags from the Build pipeline, you can simply tell the Release pipeline to deploy an older build:

1. Go to Azure DevOps -> **Pipelines**.
2. Click on the **Release Pipeline** and click **Run pipeline**.
3. Under the **Resources** section on the menu that pops up, click on `codexrelic-build-pipeline`.
4. Instead of the latest build, **select the older, stable build** you want to revert to.
5. Click **Run**. 

The pipeline will grab the exact Docker Image Tag and the exact Kubernetes manifests from that older build and push them back out to UAT -> Stage -> Prod.

---

## Method 2: Instant Kubernetes Rollback (Emergency)

Because we chose to use Kubernetes (K3s), every deployment creates a "ReplicaSet", and Kubernetes keeps a history of your previous ReplicaSets natively. 

If a deployment crashes and you need an *instant* revert (under 5 seconds) without waiting for Azure DevOps to run, you can just SSH into the VM and run the following command:

```bash
# Rollback Production to the previous version instantly
kubectl rollout undo deployment/codexrelic-api -n prod
```

Kubernetes will instantly kill the bad containers and spin the old ones back up. You can replace `-n prod` with `-n stage` or `-n uat` depending on where the emergency is.
