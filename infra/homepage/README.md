# Homepage Dashboard

Homepage is a modern, fully static, fast, secure fully proxied, highly customizable application dashboard with integrations for over 100 services.

## Deployment

Homepage is deployed via Pulumi in the `homepage.py` module and configured via the main `__main__.py` file.

## Access

Once deployed, Homepage will be available at: **http://192.168.1.50**

## Configuration

The Homepage configuration is managed via separate YAML files in the `infra/homepage/config/` directory. These files are loaded by Pulumi and deployed as a Kubernetes ConfigMap.

### Configuration Files

All configuration files are in the `infra/homepage/config/` directory:

- `kubernetes.yaml` - Kubernetes integration settings
- `settings.yaml` - Dashboard appearance, theme, and layout
- `services.yaml` - All service definitions and widgets
- `widgets.yaml` - Dashboard widgets (search, greeting, cluster info)
- `bookmarks.yaml` - Quick links and bookmarks
- `docker.yaml` - Docker integration (not used)
- `custom.css` - Custom CSS styles
- `custom.js` - Custom JavaScript

**To edit the configuration**: Simply edit these YAML files directly, then run `pulumi up` to apply changes.

### Secrets Management

**Important**: Sensitive credentials (API keys, passwords) are managed through **Pulumi secrets**, NOT hardcoded in YAML files.

See [SECRETS.md](SECRETS.md) for complete documentation on configuring secrets securely.

### Services Configuration

All your homelab services are organized into logical groups:

- **Media Services**: Jellyseerr, Bazarr
- **Downloads & Indexers**: Prowlarr, Sonarr, Radarr, Lidarr, qBittorrent, FlareSolverr
- **Monitoring & Observability**: Grafana, Loki, Mimir, Alloy
- **Infrastructure**: Longhorn, MinIO, MetalLB, Istio, Metrics Server
- **Networking & Security**: UniFi Controller, Tailscale
- **Databases**: PostgreSQL (CloudNativePG), InfluxDB

### Service Widgets

Homepage includes native integrations for many services, allowing it to display live statistics. To enable these widgets, you need to configure API keys and credentials.

#### Required API Keys and Credentials

The configuration uses environment variable placeholders that need to be set. You have two options:

##### Recommended: Use Pulumi Secrets

Configure secrets using Pulumi (encrypted, never committed to Git):

```bash
cd infra

# Set API keys as secrets
pulumi config set --secret homepage:sonarr_api_key "your-sonarr-api-key"
pulumi config set --secret homepage:radarr_api_key "your-radarr-api-key"
pulumi config set --secret homepage:lidarr_api_key "your-lidarr-api-key"
pulumi config set --secret homepage:prowlarr_api_key "your-prowlarr-api-key"
pulumi config set --secret homepage:bazarr_api_key "your-bazarr-api-key"
pulumi config set --secret homepage:jellyseerr_api_key "your-jellyseerr-api-key"
pulumi config set --secret homepage:qbittorrent_username "admin"
pulumi config set --secret homepage:qbittorrent_password "your-password"
pulumi config set --secret homepage:unifi_username "admin"
pulumi config set --secret homepage:unifi_api_key "your-unifi-api-key"

# Deploy
pulumi up
```

See [SECRETS.md](SECRETS.md) for detailed instructions on:
- How to get API keys from each service
- Verifying secrets are configured
- Updating and rotating secrets
- Security best practices

#### Alternative: Quick Testing (Not Secure)

For testing only, you can temporarily hardcode values directly in the YAML:

```bash
# Edit services.yaml
vim infra/homepage/config/services.yaml

# Replace ${SONARR_API_KEY} with actual value
# Then deploy
cd infra && pulumi up
```

**⚠️ Warning**: This is NOT recommended for production. Use Pulumi secrets instead.

#### How to Get API Keys

Most *arr applications (Sonarr, Radarr, Lidarr, Prowlarr, Bazarr):
1. Open the application web interface
2. Go to Settings → General
3. Find the "API Key" section
4. Copy the key

qBittorrent:
- Use the web UI credentials you set up

UniFi Controller:
- Use your UniFi admin credentials

Jellyseerr:
1. Open Jellyseerr
2. Go to Settings → General
3. Copy the API Key

### IP Address Reference

| Service | IP Address | Port | Protocol |
|---------|------------|------|----------|
| Homepage | 192.168.1.50 | 80 | HTTP |
| Grafana | 192.168.1.35 | 80 | HTTP |
| Prowlarr | 192.168.1.41 | 80 | HTTP |
| Jellyseerr | 192.168.1.42 | 80 | HTTP |
| Sonarr | 192.168.1.43 | 80 | HTTP |
| qBittorrent | 192.168.1.44 | 80 | HTTP |
| Bazarr | 192.168.1.45 | 80 | HTTP |
| Radarr | 192.168.1.46 | 80 | HTTP |
| Lidarr | 192.168.1.47 | 80 | HTTP |
| Home Assistant PostgreSQL | 192.168.1.48 | 5432 | TCP |
| UniFi Controller | 192.168.1.49 | 443 | HTTPS |

### Customization

To customize the Homepage configuration:

1. Edit the YAML files directly in `infra/homepage/config/`:
   - `services.yaml` - Add/remove/modify services
   - `widgets.yaml` - Configure dashboard widgets
   - `settings.yaml` - Change theme, layout, and appearance
   - `bookmarks.yaml` - Add useful links
   - `custom.css` - Add custom styles
   - `custom.js` - Add custom JavaScript
2. For services requiring API keys, use `${SECRET_NAME}` placeholder
3. Set the secret via Pulumi: `pulumi config set --secret homepage:secret_name "value"`
4. Run `pulumi up` to apply changes
5. The ConfigMap will be updated and the pod will automatically restart

**Example: Adding a new service**

1. Edit `infra/homepage/config/services.yaml`:

```yaml
- My Services:
    - New Service:
        href: http://192.168.1.100
        description: My new service
        icon: service-icon.png
        widget:
          type: service-type
          url: http://192.168.1.100
          key: ${NEW_SERVICE_API_KEY}
```

2. Set the API key as a secret:

```bash
cd infra
pulumi config set --secret homepage:new_service_api_key "your-api-key"
```

3. Update the Python code to include the new secret in `homepage.py`:

```python
secrets = {
    # ... existing secrets ...
    'NEW_SERVICE_API_KEY': config.get_secret('new_service_api_key') or '',
}
```

4. Deploy:

```bash
pulumi up
```

### Widgets

Homepage includes several useful widgets:

- **Kubernetes Cluster Widget**: Shows cluster resource usage (CPU, memory) and node status
- **Resources Widget**: Displays resource usage of the Homepage pod itself
- **Search Widget**: Quick search using DuckDuckGo
- **Greeting Widget**: Personalized welcome message

### Service Integration Features

When properly configured with API keys, Homepage can display:

- **Sonarr/Radarr/Lidarr**: Wanted, queued, and recent items
- **Prowlarr**: Number of indexers and search statistics
- **qBittorrent**: Active torrents, download/upload speeds
- **Bazarr**: Missing subtitles count
- **Jellyseerr**: Pending requests
- **Grafana**: Dashboard and alert counts
- **Longhorn**: Volume and storage statistics
- **UniFi**: Connected devices and network statistics

## Troubleshooting

### Widgets Not Showing Data

1. Check that API keys are correctly configured
2. Verify services are accessible from the Homepage pod:
   ```bash
   kubectl exec -n homepage deployment/homepage -- wget -O- http://192.168.1.43/api/v3/system/status
   ```
3. Check Homepage logs:
   ```bash
   kubectl logs -n homepage deployment/homepage
   ```

### Service Unreachable

1. Verify the service is running:
   ```bash
   kubectl get pods -A
   ```
2. Check service endpoints:
   ```bash
   kubectl get svc -A | grep <service-name>
   ```
3. Test connectivity from within the cluster:
   ```bash
   kubectl run -it --rm debug --image=nicolaka/netshoot --restart=Never -- curl http://192.168.1.43
   ```

## Documentation

- Official Homepage Documentation: https://gethomepage.dev/
- Service Widgets Guide: https://gethomepage.dev/widgets/
- Kubernetes Configuration: https://gethomepage.dev/installation/k8s/

