# Homepage Deployment Guide

## Quick Start

### 1. Deploy Homepage

From the `infra` directory, run:

```bash
pulumi up
```

This will:
- Create a `homepage` namespace
- Deploy all necessary Kubernetes resources (ServiceAccount, RBAC, ConfigMap, Deployment, Service)
- Expose Homepage at `http://192.168.1.50`

### 2. Access Homepage

Open your browser and navigate to:

```
http://192.168.1.50
```

You should see your homelab dashboard with all services organized into logical groups.

### 3. Configure Service Widgets (Optional but Recommended)

To enable live statistics for services, you need to configure API keys. You have two approaches:

#### Quick Start (Testing)

For quick testing, you can update the ConfigMap directly in Kubernetes:

```bash
kubectl edit configmap homepage -n homepage
```

Or better yet, edit the source YAML files and redeploy:

```bash
# Edit the services configuration
vim infra/homepage/services.yaml

# Apply changes
cd infra
pulumi up
```

#### Production Setup (Recommended)

1. **Collect API Keys**

   For Sonarr, Radarr, Lidarr, Prowlarr, Bazarr:
   - Open each service's web interface
   - Navigate to Settings → General → Security
   - Copy the API Key

   For qBittorrent:
   - Use your web UI username and password

   For UniFi Controller:
   - Use your UniFi admin username and API key
   - API key is required if you have MFA enabled
   - Create API key in UniFi: Settings → Admins → Your User → API Access

   For Jellyseerr:
   - Open Jellyseerr → Settings → General
   - Copy the API Key

2. **Create Secrets File**

   Create a file called `homepage-secrets.env`:

   ```bash
   HOMEPAGE_VAR_SONARR_API_KEY=your_sonarr_api_key
   HOMEPAGE_VAR_RADARR_API_KEY=your_radarr_api_key
   HOMEPAGE_VAR_LIDARR_API_KEY=your_lidarr_api_key
   HOMEPAGE_VAR_PROWLARR_API_KEY=your_prowlarr_api_key
   HOMEPAGE_VAR_BAZARR_API_KEY=your_bazarr_api_key
   HOMEPAGE_VAR_JELLYSEERR_API_KEY=your_jellyseerr_api_key
   HOMEPAGE_VAR_QBITTORRENT_USERNAME=admin
   HOMEPAGE_VAR_QBITTORRENT_PASSWORD=your_password
   HOMEPAGE_VAR_UNIFI_USERNAME=your_unifi_user
   HOMEPAGE_VAR_UNIFI_PASSWORD=your_unifi_password
   ```

3. **Create Kubernetes Secret**

   ```bash
   kubectl create secret generic homepage-secrets \
     --namespace=homepage \
     --from-env-file=homepage-secrets.env
   ```

4. **Update Deployment to Use Secrets**

   The deployment is currently configured with placeholders. To use the secrets, you would need to modify the `homepage.py` file to add environment variables from the secret. 

   Alternatively, for a simpler approach, update the ConfigMap with actual API keys (less secure but easier):

   ```bash
   kubectl edit configmap homepage -n homepage
   ```

   Replace each `{{HOMEPAGE_VAR_*}}` with the actual value.

5. **Restart Homepage**

   ```bash
   kubectl rollout restart deployment/homepage -n homepage
   ```

### 4. Verify Deployment

Check that everything is running:

```bash
# Check namespace
kubectl get namespace homepage

# Check all resources
kubectl get all -n homepage

# Check logs
kubectl logs -n homepage deployment/homepage

# Check service endpoint
kubectl get svc -n homepage
```

### 5. Test Service Connectivity

Verify Homepage can reach your services:

```bash
# From within the cluster
kubectl exec -n homepage deployment/homepage -- wget -qO- http://192.168.1.43/ping

# From your machine
curl http://192.168.1.50
```

## What Was Deployed

### Kubernetes Resources

- **Namespace**: `homepage`
- **ServiceAccount**: `homepage` (with cluster-wide read permissions)
- **Secret**: `homepage` (ServiceAccount token)
- **ClusterRole**: `homepage` (read access to namespaces, pods, nodes, ingresses, metrics)
- **ClusterRoleBinding**: Binds the ClusterRole to the ServiceAccount
- **ConfigMap**: `homepage` (contains all configuration files loaded from YAML)
- **Service**: `homepage` (LoadBalancer on 192.168.1.50:80)
- **Deployment**: `homepage` (1 replica)

### Source Configuration Files

Configuration is managed in separate YAML files in `infra/homepage/`:

1. **kubernetes.yaml**: Enables cluster mode for Kubernetes integration
2. **settings.yaml**: Dashboard appearance, theme (dark slate), layout configuration
3. **services.yaml**: All your homelab services organized into groups
4. **widgets.yaml**: Kubernetes cluster widget, resource monitoring, search
5. **bookmarks.yaml**: Quick links to documentation
6. **docker.yaml**: Docker integration (not used)
7. **custom.css**: Custom styling (add your own CSS)
8. **custom.js**: Custom JavaScript (add your own scripts)

These files are read by `homepage.py` during `pulumi up` and deployed as a ConfigMap.

### Service Groups

All services are organized into these logical groups:

1. **Media Services** (2 services)
   - Jellyseerr - Media request management
   - Bazarr - Subtitle management

2. **Downloads & Indexers** (6 services)
   - Prowlarr - Indexer manager
   - Sonarr - TV series automation
   - Radarr - Movie automation
   - Lidarr - Music automation
   - qBittorrent - BitTorrent client
   - FlareSolverr - Cloudflare bypass proxy

3. **Monitoring & Observability** (4 services)
   - Grafana - Metrics visualization
   - Loki - Log aggregation
   - Mimir - Metrics backend
   - Alloy - Metrics/logs collector

4. **Infrastructure** (5 services)
   - Longhorn - Distributed storage
   - MinIO - Object storage
   - MetalLB - Load balancer
   - Istio - Service mesh
   - Metrics Server - K8s metrics

5. **Networking & Security** (2 services)
   - UniFi Controller - Network management
   - Tailscale - VPN subnet router

6. **Databases** (2 services)
   - PostgreSQL (CloudNativePG) - Home Assistant database
   - InfluxDB - Time series database

## Customization

### Add a New Service

1. Edit `infra/homepage/services.yaml` (not the Python file!)
2. Add your service following this template:

```yaml
    - Service Name:
        href: http://service-url
        description: Service description
        icon: service-icon.png
        widget:
          type: service-type
          url: http://service-url
          key: {{HOMEPAGE_VAR_SERVICE_API_KEY}}
```

3. Apply changes:
```bash
cd infra
pulumi up
```

The changes will be automatically loaded and deployed.

### Change Theme or Layout

Edit `infra/homepage/settings.yaml`:

- **Themes**: light, dark
- **Colors**: slate, gray, zinc, neutral, stone, red, orange, amber, yellow, lime, green, emerald, teal, cyan, sky, blue, indigo, violet, purple, fuchsia, pink, rose
- **Layout**: Adjust columns per group, card blur, background image

Example:
```yaml
theme: light
color: blue
```

Then apply:
```bash
cd infra && pulumi up
```

### Add Custom CSS

Edit `infra/homepage/custom.css` to add your own styles:

```css
/* Make service cards larger */
.service-card {
  min-height: 120px;
}
```

### Add Custom JavaScript

Edit `infra/homepage/custom.js` for custom behavior:

```javascript
console.log('Homepage loaded!');
```

### Add Bookmarks

Edit `infra/homepage/bookmarks.yaml` to add frequently accessed links:

```yaml
- DevOps:
    - GitHub:
        - abbr: GH
          href: https://github.com/yourorg
```

## Monitoring

### View Logs

```bash
kubectl logs -n homepage deployment/homepage -f
```

### Check Resource Usage

```bash
kubectl top pod -n homepage
```

### Restart Homepage

```bash
kubectl rollout restart deployment/homepage -n homepage
```

## Troubleshooting

### Homepage Pod Not Starting

```bash
# Check pod status
kubectl get pods -n homepage

# Describe pod for events
kubectl describe pod -n homepage -l app.kubernetes.io/name=homepage

# Check logs
kubectl logs -n homepage -l app.kubernetes.io/name=homepage
```

### LoadBalancer IP Not Assigned

```bash
# Check MetalLB configuration
kubectl get ipaddresspools -n metallb-system

# Check service
kubectl get svc -n homepage

# Verify IP is available
kubectl get svc -A | grep 192.168.1.50
```

### Widgets Not Working

1. **API Keys**: Ensure API keys are configured correctly
2. **Network**: Verify Homepage can reach services
3. **CORS**: Some services may need CORS configuration
4. **Logs**: Check Homepage logs for errors

### Service Links Not Working

1. Verify the service IP addresses are correct
2. Test connectivity:
   ```bash
   curl http://192.168.1.43  # Example for Sonarr
   ```
3. Check if services are running:
   ```bash
   kubectl get pods -A | grep sonarr
   ```

## Updating Configuration

After making changes to any YAML file in `infra/homepage/`:

```bash
# Navigate to infra directory
cd infra

# Preview changes
pulumi preview

# Apply changes
pulumi up

# The ConfigMap will be updated and the pod will restart automatically
```

**Note**: You edit the YAML files directly - no need to modify the Python code!

## Backup

The Homepage configuration is stored in the ConfigMap. To backup:

```bash
kubectl get configmap homepage -n homepage -o yaml > homepage-backup.yaml
```

To restore:

```bash
kubectl apply -f homepage-backup.yaml
```

## Next Steps

1. **Configure API Keys**: Enable service widgets for live statistics
2. **Customize Appearance**: Adjust theme, colors, and layout to your preference
3. **Add Missing Services**: If you have services not yet listed, add them
4. **Set Up External Access**: Consider exposing Homepage via Istio ingress or Tailscale
5. **Mobile Access**: Homepage is mobile-responsive and works great on phones/tablets
6. **Pin to Browser**: Add Homepage as a home page or pinned tab for quick access

## Resources

- [Homepage Documentation](https://gethomepage.dev/)
- [Service Widgets](https://gethomepage.dev/widgets/services/)
- [Kubernetes Configuration](https://gethomepage.dev/configs/kubernetes/)
- [Homepage GitHub](https://github.com/gethomepage/homepage)

