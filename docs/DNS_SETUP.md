# Domain & DNS Setup Guide

This guide explains how to map your custom domain (`codexrelic.com`) to your newly provisioned Oracle Cloud (OCI) Kubernetes Virtual Machine.

## Prerequisites
- Your OCI VM is running.
- You know the **Public IP Address** of your VM.
  - *Current Public IP:* `129.225.82.233`
- You have access to the domain registrar where you purchased `codexrelic.com` (e.g., GoDaddy, Namecheap, Cloudflare, AWS Route 53).

## Step 1: Add DNS Records

Log into your domain registrar's DNS Management dashboard and create the following **A Records**:

### 1. Root Domain (codexrelic.com)
- **Type:** `A`
- **Name/Host:** `@` (or leave blank, depending on your registrar)
- **Value/Points To:** `129.225.82.233`
- **TTL:** `Auto` or `3600` (1 hour)

### 2. Wildcard Subdomain (Optional, for UAT/Stage)
If you want to access your different environments via subdomains like `uat.codexrelic.com` or `stage.codexrelic.com`, add a wildcard record or individual records for each environment:
- **Type:** `A`
- **Name/Host:** `*` (or `uat`, `stage`, `api`)
- **Value/Points To:** `129.225.82.233`
- **TTL:** `Auto` or `3600`

## Step 2: Wait for DNS Propagation

DNS changes can take anywhere from 5 minutes to 48 hours to propagate globally. You can verify the propagation status using tools like [DNS Checker](https://dnschecker.org/#A/codexrelic.com).

To check locally on your terminal, run:
```bash
ping codexrelic.com
```
It should return replies from `129.225.82.233`.

## Step 3: Configure Ingress (HTTPS)

Once DNS is fully propagated, you can configure an Ingress Controller (like Traefik, which comes built-in with K3s) and `cert-manager` to automatically provision free Let's Encrypt SSL certificates for your domain.

*Note: Do not attempt to provision Let's Encrypt certificates before DNS has propagated, or you may hit API rate limits from failed validation attempts.*
