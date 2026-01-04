# Homepage Dashboard - Homelab Summary

## 🎉 Deployment Complete!

Homepage has been successfully configured and is ready to deploy to your Kubernetes cluster.

## 📍 Access Information

**Homepage URL**: `http://192.168.1.50`

Once deployed, visit this URL to see your complete homelab dashboard.

## 🏠 Your Homelab At a Glance

### Network Map (192.168.1.x)

```
┌─────────────────────────────────────────────────────────────────┐
│                     Home Automation Lab                          │
│                    Kubernetes Cluster                            │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ 📊 MONITORING & OBSERVABILITY                                    │
├─────────────────────────────────────────────────────────────────┤
│ • Grafana              → http://192.168.1.35                     │
│ • Loki                 → loki-gateway.loki.svc.cluster.local     │
│ • Mimir                → mimir-nginx.mimir.svc.cluster.local     │
│ • Alloy                → 192.168.1.39 (Mimir), 192.168.1.36 (Loki)│
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ 🎬 MEDIA SERVICES                                                │
├─────────────────────────────────────────────────────────────────┤
│ • Jellyseerr           → http://192.168.1.42                     │
│ • Bazarr               → http://192.168.1.45                     │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ ⬇️  DOWNLOADS & INDEXERS                                         │
├─────────────────────────────────────────────────────────────────┤
│ • Prowlarr             → http://192.168.1.41                     │
│ • Sonarr (TV)          → http://192.168.1.43                     │
│ • Radarr (Movies)      → http://192.168.1.46                     │
│ • Lidarr (Music)       → http://192.168.1.47                     │
│ • qBittorrent          → http://192.168.1.44                     │
│ • FlareSolverr         → flaresolverr.arr-stack.svc.cluster.local│
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ 🔧 INFRASTRUCTURE                                                │
├─────────────────────────────────────────────────────────────────┤
│ • Longhorn             → longhorn-frontend.longhorn-system.svc   │
│ • MinIO                → minio.minio.svc.cluster.local:9000      │
│ • MetalLB              → Load Balancer (192.168.1.x pool)        │
│ • Istio                → Service Mesh                            │
│ • Metrics Server       → Kubernetes Metrics API                  │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ 🌐 NETWORKING & SECURITY                                         │
├─────────────────────────────────────────────────────────────────┤
│ • UniFi Controller     → https://192.168.1.49                    │
│ • Tailscale            → VPN Subnet Router                       │
│ • Raspberry Pi         → http://192.168.1.214 (Wall Display +    │
│                          Zigbee2MQTT)                            │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ 🗄️  DATABASES                                                    │
├─────────────────────────────────────────────────────────────────┤
│ • PostgreSQL (CNPG)    → 192.168.1.48:5432 (Home Assistant)      │
│ • InfluxDB             → influxdb.home-automation.svc:8086       │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ 📊 HOMEPAGE DASHBOARD  → http://192.168.1.50                     │
└─────────────────────────────────────────────────────────────────┘
```

## 📋 Complete Service Inventory

| Service | Category | IP/URL | Port | Features |
|---------|----------|--------|------|----------|
| Homepage | Dashboard | 192.168.1.50 | 80 | Service dashboard with widgets |
| Grafana | Monitoring | 192.168.1.35 | 80 | Metrics visualization |
| Prowlarr | Downloads | 192.168.1.41 | 80 | Indexer management |
| Jellyseerr | Media | 192.168.1.42 | 80 | Media requests |
| Sonarr | Downloads | 192.168.1.43 | 80 | TV series automation |
| qBittorrent | Downloads | 192.168.1.44 | 80 | Torrent client |
| Bazarr | Media | 192.168.1.45 | 80 | Subtitle management |
| Radarr | Downloads | 192.168.1.46 | 80 | Movie automation |
| Lidarr | Downloads | 192.168.1.47 | 80 | Music automation |
| PostgreSQL | Database | 192.168.1.48 | 5432 | Home Assistant DB |
| UniFi | Networking | 192.168.1.49 | 443 | Network controller |
| Raspberry Pi | Edge Device | 192.168.1.214 | 80 | Wall display + Zigbee2MQTT |

## 🎨 Dashboard Features

### Integrated Widgets

Homepage includes native integrations for all your *arr services:

- **Live Statistics**: Real-time data from services (requires API keys)
- **Sonarr/Radarr/Lidarr**: Shows wanted items, queue status, recent activity
- **Prowlarr**: Indexer count and health
- **qBittorrent**: Active torrents, speeds, total downloaded
- **Bazarr**: Missing subtitles count
- **Jellyseerr**: Pending requests
- **Grafana**: Dashboard and alert counts
- **UniFi**: Connected devices and network stats
- **Longhorn**: Storage volume statistics
- **Kubernetes**: Cluster resource usage and node status

### Dashboard Layout

Services are organized into 6 logical groups:

1. **Media Services** (Row layout, 3 columns)
2. **Downloads & Indexers** (Row layout, 3 columns)
3. **Monitoring & Observability** (Row layout, 3 columns)
4. **Infrastructure** (Row layout, 3 columns)
5. **Networking & Security** (Row layout, 2 columns)
6. **Databases** (Row layout, 2 columns)

### Visual Design

- **Theme**: Dark mode with slate color scheme
- **Background**: Modern blurred gradient
- **Cards**: Glass-morphism effect with slight blur
- **Icons**: Official service icons
- **Layout**: Responsive design works on desktop, tablet, and mobile

### Additional Features

- **Search Bar**: Quick web search with DuckDuckGo
- **Bookmarks**: Quick access to documentation (Kubernetes, Helm, Pulumi, Home Assistant, etc.)
- **Welcome Message**: Personalized greeting
- **Resource Monitor**: Shows Homepage's own CPU and memory usage
- **Kubernetes Widget**: Displays cluster and node statistics
- **Logo**: Home Assistant icon as main logo

## 🚀 Deployment Steps

### 1. Deploy to Kubernetes

```bash
cd /Users/pawelrosinski/x/home-automation/infra
pulumi up
```

### 2. Verify Deployment

```bash
# Check resources
kubectl get all -n homepage

# View logs
kubectl logs -n homepage deployment/homepage -f

# Verify service
kubectl get svc -n homepage
```

### 3. Access Dashboard

Open browser to: `http://192.168.1.50`

### 4. Configure Widgets (Optional)

To enable live statistics:

1. Get API keys from each service (Settings → General → API Key)
2. Edit the services configuration:
   ```bash
   vim infra/homepage/services.yaml
   ```
3. Replace `{{HOMEPAGE_VAR_*}}` placeholders with actual keys
4. Apply changes:
   ```bash
   cd infra && pulumi up
   ```

## 📁 Files Created

```
/Users/pawelrosinski/x/home-automation/
├── infra/
│   ├── __main__.py                 (Updated: Added Homepage import and deployment)
│   └── homepage/
│       ├── __init__.py             (New: Python module init)
│       ├── homepage.py             (New: Main Pulumi deployment code)
│       │
│       ├── kubernetes.yaml         (New: K8s cluster mode config)
│       ├── settings.yaml           (New: Theme, layout, appearance)
│       ├── services.yaml           (New: All service definitions)
│       ├── widgets.yaml            (New: Dashboard widgets)
│       ├── bookmarks.yaml          (New: Quick links)
│       ├── docker.yaml             (New: Docker config - empty)
│       ├── custom.css              (New: Custom styles)
│       ├── custom.js               (New: Custom JavaScript)
│       │
│       ├── README.md               (New: Configuration guide)
│       ├── DEPLOYMENT.md           (New: Deployment guide)
│       ├── QUICKSTART.md           (New: 5-minute quick start)
│       └── ARCHITECTURE.md         (New: System architecture)
└── HOMEPAGE_SUMMARY.md             (New: This file)
```

## 🔑 API Key Configuration

To enable service widgets, you'll need API keys from:

### Required API Keys

1. **Sonarr** - Settings → General → Security → API Key
2. **Radarr** - Settings → General → Security → API Key
3. **Lidarr** - Settings → General → Security → API Key
4. **Prowlarr** - Settings → General → Security → API Key
5. **Bazarr** - Settings → General → Security → API Key
6. **Jellyseerr** - Settings → General → API Key
7. **qBittorrent** - Web UI username and password
8. **UniFi Controller** - Admin username and API key (works with MFA!)

### Quick Configuration Command

Once you have all keys, create them as a secret:

```bash
kubectl create secret generic homepage-secrets \
  --namespace=homepage \
  --from-literal=HOMEPAGE_VAR_SONARR_API_KEY='your-key' \
  --from-literal=HOMEPAGE_VAR_RADARR_API_KEY='your-key' \
  --from-literal=HOMEPAGE_VAR_LIDARR_API_KEY='your-key' \
  --from-literal=HOMEPAGE_VAR_PROWLARR_API_KEY='your-key' \
  --from-literal=HOMEPAGE_VAR_BAZARR_API_KEY='your-key' \
  --from-literal=HOMEPAGE_VAR_JELLYSEERR_API_KEY='your-key' \
  --from-literal=HOMEPAGE_VAR_QBITTORRENT_USERNAME='admin' \
  --from-literal=HOMEPAGE_VAR_QBITTORRENT_PASSWORD='your-password' \
  --from-literal=HOMEPAGE_VAR_UNIFI_USERNAME='admin' \
  --from-literal=HOMEPAGE_VAR_UNIFI_API_KEY='your-unifi-api-key'
```

Then update the ConfigMap to use actual values instead of placeholders.

## 🎯 Next Steps

1. **Deploy Homepage**: Run `pulumi up` to deploy
2. **Access Dashboard**: Open http://192.168.1.50
3. **Configure API Keys**: Enable live widgets
4. **Customize Theme**: Adjust colors/layout to your preference
5. **Add More Services**: If you have additional services, add them to the config
6. **Mobile Bookmark**: Add to your phone's home screen for quick access
7. **Set as Browser Home**: Use as your default browser landing page

## 🔗 Useful Links

- **Homepage Documentation**: https://gethomepage.dev/
- **Service Widgets Guide**: https://gethomepage.dev/widgets/services/
- **Kubernetes Integration**: https://gethomepage.dev/configs/kubernetes/
- **GitHub Repository**: https://github.com/gethomepage/homepage

## 💡 Pro Tips

1. **Pin to Browser Tab**: Homepage makes a great pinned tab
2. **Mobile Access**: Works great on phones - consider adding to home screen
3. **Bookmarks**: Use the search bar for quick web searches
4. **Widgets**: Service widgets update automatically every few seconds
5. **Customization**: The dark theme and background can be changed in settings
6. **Multiple Devices**: Access from any device on your network
7. **Monitoring**: Use the Kubernetes widget to monitor cluster health

## 🆘 Support

For issues or questions:

1. Check logs: `kubectl logs -n homepage deployment/homepage`
2. Review configuration: `kubectl get configmap homepage -n homepage -o yaml`
3. Verify connectivity: Test service URLs from the Homepage pod
4. Consult documentation: https://gethomepage.dev/

---

**Enjoy your new homelab dashboard! 🎉**

You now have a beautiful, functional dashboard that shows all your homelab services in one place with live statistics and easy access to everything you need.

