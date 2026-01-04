# Homepage Architecture

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                          External Access                             │
│                     http://192.168.1.50                              │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         MetalLB LoadBalancer                         │
│                      (IP: 192.168.1.50:80)                           │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    Kubernetes Service (homepage)                     │
│                    Namespace: homepage                               │
│                    Type: LoadBalancer                                │
│                    Port: 80 → TargetPort: 3000                       │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      Deployment (homepage)                           │
│                      Replicas: 1                                     │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │              Pod: homepage-xxxxx                               │  │
│  │  ┌─────────────────────────────────────────────────────────┐  │  │
│  │  │  Container: homepage                                     │  │  │
│  │  │  Image: ghcr.io/gethomepage/homepage:latest             │  │  │
│  │  │  Port: 3000                                              │  │  │
│  │  │  Resources:                                              │  │  │
│  │  │    Requests: 100m CPU, 128Mi Memory                     │  │  │
│  │  │    Limits: 500m CPU, 512Mi Memory                       │  │  │
│  │  └─────────────────────────────────────────────────────────┘  │  │
│  │                                                                │  │
│  │  Volume Mounts:                                                │  │
│  │  • /app/config/* → ConfigMap (homepage)                       │  │
│  │  • /app/config/logs → emptyDir                                │  │
│  └───────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    ConfigMap (homepage)                              │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │  • kubernetes.yaml   - K8s cluster mode config                │  │
│  │  • settings.yaml     - Dashboard theme and layout             │  │
│  │  • services.yaml     - All service definitions                │  │
│  │  • widgets.yaml      - Dashboard widgets                      │  │
│  │  • bookmarks.yaml    - Quick links                            │  │
│  │  • docker.yaml       - Docker config (empty)                  │  │
│  │  • custom.css        - Custom styles (empty)                  │  │
│  │  • custom.js         - Custom scripts (empty)                 │  │
│  └───────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                 RBAC (ServiceAccount + ClusterRole)                  │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │  ServiceAccount: homepage                                     │  │
│  │  • Mounted in pod for K8s API access                          │  │
│  │                                                                │  │
│  │  ClusterRole: homepage                                        │  │
│  │  Permissions (read-only):                                     │  │
│  │  • namespaces, pods, nodes                                    │  │
│  │  • ingresses (networking.k8s.io, traefik.io)                 │  │
│  │  • httproutes, gateways (gateway.networking.k8s.io)          │  │
│  │  • metrics (metrics.k8s.io)                                   │  │
│  │                                                                │  │
│  │  ClusterRoleBinding: homepage                                 │  │
│  │  • Binds ClusterRole to ServiceAccount                        │  │
│  └───────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
```

## Service Communication Flow

```
┌──────────────────┐
│   User Browser   │
│  192.168.1.x     │
└────────┬─────────┘
         │ HTTP GET http://192.168.1.50
         ▼
┌──────────────────────────────────────────────────────────────┐
│                    Homepage Dashboard                         │
│               (Serves static HTML/CSS/JS)                     │
└────────┬─────────────────────────────────────────────────────┘
         │
         │ Client-side requests to services
         │
         ├──────────────────────────────────────────────────────┐
         │                                                       │
         ▼                                                       ▼
┌─────────────────────┐                          ┌────────────────────────┐
│   ARR Stack         │                          │  Monitoring Stack      │
│                     │                          │                        │
│ • Prowlarr    :41   │                          │ • Grafana        :35   │
│ • Jellyseerr  :42   │                          │ • Loki (internal)      │
│ • Sonarr      :43   │                          │ • Mimir (internal)     │
│ • qBittorrent :44   │                          │ • Alloy          :39   │
│ • Bazarr      :45   │                          └────────────────────────┘
│ • Radarr      :46   │                                     │
│ • Lidarr      :47   │                                     │
└─────────────────────┘                                     │
         │                                                  │
         │                                                  │
         ▼                                                  ▼
┌─────────────────────┐                          ┌────────────────────────┐
│ Infrastructure      │                          │  Networking            │
│                     │                          │                        │
│ • Longhorn (int.)   │                          │ • UniFi         :49    │
│ • MinIO (int.)      │                          │ • Tailscale            │
│ • MetalLB           │                          └────────────────────────┘
│ • Istio             │
│ • Metrics Server    │                          ┌────────────────────────┐
└─────────────────────┘                          │  Databases             │
                                                  │                        │
                                                  │ • PostgreSQL    :48    │
                                                  │ • InfluxDB (int.)      │
                                                  └────────────────────────┘
```

## Kubernetes API Access

```
┌──────────────────────────────────────────────────────────────────┐
│                    Homepage Pod                                   │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │  Uses ServiceAccount token to access K8s API               │  │
│  └────────────┬───────────────────────────────────────────────┘  │
└───────────────┼──────────────────────────────────────────────────┘
                │
                ▼
┌──────────────────────────────────────────────────────────────────┐
│                Kubernetes API Server                              │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │  Validates ServiceAccount token                            │  │
│  │  Checks RBAC permissions (ClusterRole)                     │  │
│  │  Returns requested data if authorized                      │  │
│  └────────────────────────────────────────────────────────────┘  │
└────────────────┬─────────────────────────────────────────────────┘
                 │
                 ▼
┌──────────────────────────────────────────────────────────────────┐
│           Data Retrieved by Homepage                              │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │  • Cluster metrics (CPU, memory usage)                     │  │
│  │  • Node information and status                             │  │
│  │  • Pod counts and health                                   │  │
│  │  • Namespace information                                   │  │
│  │  • Ingress configurations                                  │  │
│  │  • Service discovery                                       │  │
│  └────────────────────────────────────────────────────────────┘  │
│                                                                   │
│  Displayed in Kubernetes Widget on Dashboard                     │
└──────────────────────────────────────────────────────────────────┘
```

## Data Flow for Service Widgets

```
┌──────────────────┐
│   User Browser   │
└────────┬─────────┘
         │ 1. Load Homepage
         ▼
┌──────────────────────────────────────────┐
│         Homepage (Static App)             │
│  • Renders HTML/CSS                       │
│  • Loads service configuration            │
│  • Initializes widget JavaScript          │
└────────┬─────────────────────────────────┘
         │ 2. JavaScript makes API calls
         │    (with API keys from config)
         ▼
┌──────────────────────────────────────────┐
│      Service APIs (e.g., Sonarr)         │
│  http://192.168.1.43/api/v3/system       │
│  • Returns JSON data                      │
│  • Requires API key authentication        │
└────────┬─────────────────────────────────┘
         │ 3. Returns data to browser
         ▼
┌──────────────────────────────────────────┐
│     Homepage JavaScript Widgets          │
│  • Parses API responses                   │
│  • Updates widget display                 │
│  • Auto-refreshes every few seconds       │
└──────────────────────────────────────────┘
```

## Configuration Management

```
┌─────────────────────────────────────────────────────────────┐
│                   Pulumi (IaC)                               │
│  File: infra/homepage/homepage.py                            │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  Python code defines:                                 │  │
│  │  • Kubernetes resources                               │  │
│  │  • ConfigMap with YAML configs                        │  │
│  │  • RBAC permissions                                   │  │
│  │  • Service and Deployment specs                       │  │
│  └────────────────────┬──────────────────────────────────┘  │
└─────────────────────────┼──────────────────────────────────┘
                          │ pulumi up
                          ▼
┌─────────────────────────────────────────────────────────────┐
│              Kubernetes Cluster State                        │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  • Namespace: homepage                                │  │
│  │  • ConfigMap: homepage (with all YAML files)          │  │
│  │  • ServiceAccount: homepage                           │  │
│  │  • Secret: homepage (token)                           │  │
│  │  • ClusterRole: homepage                              │  │
│  │  • ClusterRoleBinding: homepage                       │  │
│  │  • Service: homepage (LoadBalancer)                   │  │
│  │  • Deployment: homepage (1 replica)                   │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                          │
                          │ ConfigMap mounted as files
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                Homepage Container                            │
│  /app/config/                                                │
│  ├── kubernetes.yaml                                         │
│  ├── settings.yaml                                           │
│  ├── services.yaml                                           │
│  ├── widgets.yaml                                            │
│  ├── bookmarks.yaml                                          │
│  ├── docker.yaml                                             │
│  ├── custom.css                                              │
│  └── custom.js                                               │
└─────────────────────────────────────────────────────────────┘
```

## Update Flow

```
┌────────────────────────────────────────────────────────────────┐
│  Step 1: Edit Configuration                                     │
│  • Modify infra/homepage/homepage.py                            │
│  • Update ConfigMap data section                                │
└────────────────────┬───────────────────────────────────────────┘
                     │
                     ▼
┌────────────────────────────────────────────────────────────────┐
│  Step 2: Preview Changes                                        │
│  $ pulumi preview                                               │
│  • Shows what will change                                       │
└────────────────────┬───────────────────────────────────────────┘
                     │
                     ▼
┌────────────────────────────────────────────────────────────────┐
│  Step 3: Apply Changes                                          │
│  $ pulumi up                                                    │
│  • Updates ConfigMap in Kubernetes                              │
└────────────────────┬───────────────────────────────────────────┘
                     │
                     ▼
┌────────────────────────────────────────────────────────────────┐
│  Step 4: Automatic Restart (if ConfigMap changed)               │
│  • Kubernetes detects ConfigMap change                          │
│  • Rolling update of deployment                                 │
│  • Pod restarts with new configuration                          │
└────────────────────┬───────────────────────────────────────────┘
                     │
                     ▼
┌────────────────────────────────────────────────────────────────┐
│  Step 5: Changes Live                                           │
│  • Refresh browser to see updates                               │
│  • New configuration active                                     │
└────────────────────────────────────────────────────────────────┘
```

## Security Model

```
┌─────────────────────────────────────────────────────────────────┐
│                   Security Layers                                │
│                                                                  │
│  1. Network Security                                             │
│     • Homepage exposed only on local network (192.168.1.x)       │
│     • LoadBalancer type (no external internet exposure)          │
│     • Services communicate within cluster or via internal IPs    │
│                                                                  │
│  2. Kubernetes RBAC                                              │
│     • ServiceAccount with limited read-only permissions          │
│     • ClusterRole grants minimal required access                 │
│     • No write/delete permissions on cluster resources           │
│                                                                  │
│  3. API Authentication                                           │
│     • Service API keys stored in ConfigMap (consider Secrets)    │
│     • Each service validates its own API key                     │
│     • Browser makes direct API calls (client-side)               │
│                                                                  │
│  4. Container Security                                           │
│     • Official Homepage image from GitHub Container Registry     │
│     • Resource limits prevent resource exhaustion                │
│     • emptyDir for logs (no persistent sensitive data)           │
│                                                                  │
│  5. Configuration Security                                       │
│     • ConfigMap in Kubernetes (cluster access required)          │
│     • Consider moving API keys to Secrets for production         │
│     • No hardcoded credentials in code                           │
└─────────────────────────────────────────────────────────────────┘
```

## Resource Requirements

```
┌─────────────────────────────────────────────────────────────────┐
│                 Resource Allocation                              │
│                                                                  │
│  Homepage Pod:                                                   │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  Requests:                                                 │  │
│  │    CPU:    100m  (0.1 core)                                │  │
│  │    Memory: 128Mi                                           │  │
│  │                                                            │  │
│  │  Limits:                                                   │  │
│  │    CPU:    500m  (0.5 core)                                │  │
│  │    Memory: 512Mi                                           │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                  │
│  Storage:                                                        │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  ConfigMap: ~15KB (YAML configuration)                     │  │
│  │  Logs:      emptyDir (ephemeral, cleared on pod restart)   │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                  │
│  Network:                                                        │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  LoadBalancer: 1 IP address (192.168.1.50)                 │  │
│  │  Port: 80 (HTTP)                                           │  │
│  └───────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

## High Availability Considerations

```
┌─────────────────────────────────────────────────────────────────┐
│           Current Setup (Single Replica)                         │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  Pros:                                                     │  │
│  │  • Simple configuration                                    │  │
│  │  • Low resource usage                                      │  │
│  │  • Sufficient for homelab                                  │  │
│  │                                                            │  │
│  │  Cons:                                                     │  │
│  │  • Downtime during updates                                 │  │
│  │  • No redundancy if pod fails                              │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                  │
│           Optional: Multiple Replicas                            │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  To enable HA:                                             │  │
│  │  1. Set replicas: 2 or 3                                   │  │
│  │  2. Enable sticky sessions on LoadBalancer                 │  │
│  │     (prevents unnecessary re-renders)                      │  │
│  │  3. Use RollingUpdate strategy                             │  │
│  │  4. Configure PodDisruptionBudget                          │  │
│  └───────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

## Integration Architecture

```
Homepage Dashboard
       │
       ├─── Kubernetes API (via ServiceAccount)
       │    ├─── Cluster metrics
       │    ├─── Node information
       │    └─── Pod status
       │
       ├─── ARR Stack Services (via HTTP APIs)
       │    ├─── Sonarr API
       │    ├─── Radarr API
       │    ├─── Lidarr API
       │    ├─── Prowlarr API
       │    ├─── Bazarr API
       │    ├─── Jellyseerr API
       │    └─── qBittorrent API
       │
       ├─── Monitoring Stack (via HTTP APIs)
       │    ├─── Grafana API
       │    ├─── Loki (health checks)
       │    └─── Mimir (health checks)
       │
       ├─── Infrastructure (via HTTP/Ping)
       │    ├─── Longhorn API
       │    └─── MinIO health endpoints
       │
       └─── Networking (via HTTP APIs)
            ├─── UniFi Controller API
            └─── Service health checks
```

This architecture provides:
- **Modularity**: Each component is independently deployable
- **Scalability**: Can add more services easily
- **Maintainability**: Configuration as code via Pulumi
- **Observability**: Integrates with your monitoring stack
- **Security**: Minimal permissions, network isolation
- **Flexibility**: Easy to customize and extend

