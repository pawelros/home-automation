# External-DNS

External-DNS automatically synchronizes exposed Kubernetes Services and Ingresses with your Pi-hole DNS server.

## Configuration

External-DNS is configured to:
- **Automatically create DNS records for all LoadBalancer services** (no annotations required)
- Monitor Kubernetes Services and Ingresses
- Update DNS records in Pi-hole automatically
- Use TXT records to track ownership of DNS records
- Sync changes every minute
- Use `.lab` domain for all services (`.local` is reserved for mDNS and causes conflicts)

## Migration from Helm Chart

If you're migrating from the Helm chart to plain Kubernetes manifests, you need to delete the Helm release first:

```bash
helm uninstall external-dns -n external-dns
# Delete the old secret if it exists (leftover from Helm chart)
kubectl delete secret external-dns-pihole-secret -n external-dns
# Optionally delete the namespace for a clean slate
kubectl delete namespace external-dns
```

Then deploy with `pulumi up`.

**Note**: The new deployment uses the secret name `pihole-password` (matching the official tutorial). Any old secrets with different names should be cleaned up.

## Setup

Before deploying, you need to set the Pi-hole password as a Pulumi secret. For Pi-hole v6, use the **admin password** (API keys are deprecated in v6).

**Recommended (for Pi-hole v6):**
```bash
cd infra
pulumi config set --secret external-dns:pihole_password "your-pihole-admin-password"
```

**Alternative (fallback to Homepage API key):**
If you prefer to use the same secret as Homepage (for Pi-hole v5 or if API key still works):
```bash
cd infra
pulumi config set --secret homepage:pihole_api_key "your-pihole-api-key"
```

**Note**: 
- For Pi-hole v6: Use admin password (recommended)
- For Pi-hole v5: API key or password both work
- The configuration will check `external-dns:pihole_password` first, then fall back to `homepage:pihole_api_key`

## Pi-hole Requirements

- Pi-hole version 6.0 or newer (API v6)
- Pi-hole server accessible at the configured URL (default: `http://192.168.1.3`)
- Admin password for API access

## How It Works

1. External-DNS watches for Services and Ingresses
2. **For LoadBalancer services**: Automatically creates DNS records using the pattern `{service-name}.lab`
3. **For annotated services**: Uses the hostname specified in the annotation
4. It uses TXT records to track which records it manages
5. When resources are deleted, it removes the corresponding DNS records

## Automatic DNS Records

All LoadBalancer services automatically get DNS records created. The following services have been configured with friendly hostnames:

- `prowlarr.lab` → 192.168.1.41
- `sonarr.lab` → 192.168.1.43
- `radarr.lab` → 192.168.1.46
- `lidarr.lab` → 192.168.1.47
- `bazarr.lab` → 192.168.1.45
- `qbittorrent.lab` → 192.168.1.44
- `jellyseerr.lab` → 192.168.1.42
- `grafana.lab` → 192.168.1.35
- `homepage.lab` → 192.168.1.50
- `unifi.lab` → 192.168.1.29
- `postgres.lab` → 192.168.1.48

## Custom Hostnames

To specify a custom hostname for a service, add the annotation:

```yaml
annotations:
  external-dns.alpha.kubernetes.io/hostname: "custom-name.lab"
  external-dns.alpha.kubernetes.io/ttl: "300"  # Optional: TTL in seconds
```

## Verification

Check external-dns logs:

```bash
kubectl logs -n external-dns deployment/external-dns -f
```

Check Pi-hole DNS records in the admin panel or test DNS resolution:

```bash
nslookup prowlarr.lab
ping sonarr.lab
```

