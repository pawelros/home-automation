# Homepage Quick Start

## 🚀 5-Minute Deployment

### Step 1: Deploy (30 seconds)

```bash
cd /Users/pawelrosinski/x/home-automation/infra
pulumi up
```

Type `yes` when prompted.

### Step 2: Wait for Deployment (1-2 minutes)

Watch the deployment progress. Pulumi will create:
- Namespace
- ServiceAccount and RBAC
- ConfigMap with all configuration
- Deployment with Homepage pod
- LoadBalancer Service

### Step 3: Access Homepage (immediately)

Open your browser:

```
http://192.168.1.50
```

**That's it!** 🎉 Your dashboard is live!

## What You'll See

Your homepage will display:

✅ **6 Service Groups** organized logically
✅ **Kubernetes cluster widget** showing resource usage  
✅ **Search bar** for quick web searches
✅ **Bookmarks** to useful documentation
✅ **All your services** with descriptions and icons

## Optional: Enable Live Widgets (5 minutes)

To show live statistics from your services:

### Quick Method

1. Get API keys from your services:
   - Open each *arr service (Sonarr, Radarr, etc.)
   - Go to: Settings → General → Security
   - Copy the API Key

2. Edit the services configuration file:
   ```bash
   vim infra/homepage/services.yaml
   # or use your preferred editor
   code infra/homepage/services.yaml
   ```

3. Find and replace these placeholders with actual keys:
   ```yaml
   # Find:
   key: {{HOMEPAGE_VAR_SONARR_API_KEY}}
   
   # Replace with:
   key: your-actual-api-key-here
   ```

4. Save the file

5. Apply the changes:
   ```bash
   cd infra
   pulumi up
   ```

6. Wait for deployment to complete (30 seconds)

7. Refresh your browser - widgets now show live data!

## Troubleshooting

### Pod Not Starting?

```bash
kubectl get pods -n homepage
kubectl logs -n homepage deployment/homepage
```

### IP Not Assigned?

```bash
kubectl get svc -n homepage
```

Should show `192.168.1.50` as EXTERNAL-IP.

### Can't Access Dashboard?

1. Check MetalLB is running:
   ```bash
   kubectl get pods -n metallb-system
   ```

2. Verify IP not in use:
   ```bash
   kubectl get svc -A | grep 192.168.1.50
   ```

3. Test from cluster:
   ```bash
   kubectl run -it --rm debug --image=curlimages/curl --restart=Never -- \
     curl http://homepage.homepage.svc.cluster.local
   ```

### Getting "Host validation failed"?

This means the IP/hostname you're using isn't allowed. The deployment includes:
- `192.168.1.50` (LoadBalancer IP)
- `homepage` and cluster DNS names
- `localhost`

If you need to add more (e.g., custom domain, Tailscale hostname):

1. Edit `homepage.py` and add to `HOMEPAGE_ALLOWED_HOSTS`
2. Run `pulumi up`

## Next Steps

- 📝 Read [DEPLOYMENT.md](DEPLOYMENT.md) for detailed configuration
- 🏗️ Check [ARCHITECTURE.md](ARCHITECTURE.md) to understand the system
- 📚 Review [README.md](README.md) for API key configuration
- 🎨 Customize theme and layout in ConfigMap

## Useful Commands

```bash
# View logs
kubectl logs -n homepage deployment/homepage -f

# Check status
kubectl get all -n homepage

# Edit configuration (recommended - edit YAML files then redeploy)
vim infra/homepage/services.yaml
cd infra && pulumi up

# Edit configuration (alternative - directly in cluster, lost on next pulumi up)
kubectl edit configmap homepage -n homepage

# Manual restart (usually not needed, happens automatically)
kubectl rollout restart deployment/homepage -n homepage

# Delete (if needed)
kubectl delete namespace homepage
```

## Support

- Homepage Docs: https://gethomepage.dev/
- Service Widgets: https://gethomepage.dev/widgets/services/
- GitHub Issues: https://github.com/gethomepage/homepage/issues

---

**Enjoy your homelab dashboard!** 🏠✨

