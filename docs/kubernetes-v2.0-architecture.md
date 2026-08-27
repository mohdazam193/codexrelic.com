# Kubernetes Deployment Version 2.0

## Overview
This document outlines the architecture and deployment strategy for the new generation of our Kubernetes deployment, referred to as **Version 2.0**. 

Our previous deployment strategy relied on standard Kubernetes `Deployment` resources, which inherently execute Rolling Updates. While standard, this lacked advanced traffic shaping and safety mechanisms required for high-availability production environments.

Version 2.0 introduces three major pillars of improvement:
1. **Zero-Downtime Blue/Green Deployments (Argo Rollouts)**
2. **Gradual and Stabilized Autoscaling (HPA Behavior)**
3. **Hardened Security Posture (Docker Multi-stage & Non-root)**

---

## 1. Blue/Green Deployment Strategy
We have transitioned from standard Kubernetes `Deployment` objects to **Argo Rollouts** (`Rollout` custom resource).

### Why it was done:
Previously, our Azure DevOps pipeline triggered automatically upon a new image push to Docker Hub, immediately updating the live cluster. This "Rolling Update" approach meant that if a buggy image was deployed, production users would instantly experience errors until a rollback could be issued.

### What it achieves:
- **Safe Automatic Triggers:** Azure DevOps still triggers automatically and applies the new manifest, but the new version is spun up in a completely isolated "Green" environment in the background.
- **Preview Testing:** A dedicated `previewService` allows developers and QA to test the new code against the live database *before* any public traffic hits it.
- **Instant Switch:** Once the green environment is verified, a single "promote" action instantly switches all production traffic over. If an issue is found *after* promotion, traffic can be instantly routed back to the "Blue" environment without waiting for pods to terminate and recreate.

## 2. Gradual Autoscaling Stabilization
Our HorizontalPodAutoscaler (HPA) has been upgraded with custom `behavior` policies.

### Why it was done:
Traffic spikes can cause erratic scaling behavior ("thrashing" or "flapping"), where the cluster rapidly scales up and down within seconds. This can lead to resource exhaustion, API rate limits being hit, and an unstable user experience.

### What it achieves:
- **Gradual Scale-Up:** Prevents the system from provisioning too many pods at once by limiting the maximum scale-up rate (e.g., maximum 2 pods per 60 seconds).
- **Gradual Scale-Down:** Prevents aggressively terminating pods the moment traffic drops, ensuring that sudden secondary spikes don't hit a degraded cluster.
- **5-Minute Stabilization Window:** Ensures the scaling decision is calculated over a rolling 5-minute window, effectively ignoring split-second anomalies.

## 3. Docker Image Hardening
The application container image has been overhauled to use multi-stage builds and a restricted execution context.

### Why it was done:
Running containers as the `root` user and shipping build utilities (like `gcc`, compilers, and source headers) inside production containers presents a massive security risk. If an attacker gains Remote Code Execution (RCE), they have root access to the container filesystem and all the tools needed to download secondary payloads or compile exploits.

### What it achieves:
- **Reduced Attack Surface:** Multi-stage builds compile all dependencies in an intermediate layer and only copy the compiled binaries to the final image. Build tools are never shipped to production.
- **Principle of Least Privilege:** The application runs as an unprivileged, restricted user (`appuser`). Even if a vulnerability is exploited, the attacker cannot modify system files, install packages, or easily break out of the container context.
