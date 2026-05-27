# mDNS Publisher

Automatically publishes Kubernetes LoadBalancer services via mDNS (Multicast DNS) so they can be discovered using `.local` hostnames.

## How It Works

The mDNS publisher watches all Kubernetes services and automatically publishes LoadBalancer services that have:
- The annotation `external-dns.alpha.kubernetes.io/hostname` (auto-published)
- OR the annotation `mdns.alpha.kubernetes.io/publish: "true"` (explicit)

Services are published as `{hostname}.local` where the hostname is extracted from:
1. `mdns.alpha.kubernetes.io/hostname` annotation (preferred)
2. `external-dns.alpha.kubernetes.io/hostname` annotation (fallback)
3. `{service-name}.local` (default)

## Features

- **Automatic Discovery**: Services with external-dns annotations are automatically published
- **HTTP Service Discovery**: Publishes `_http._tcp` services for web-based services
- **Dynamic Updates**: Automatically adds/removes services as they are created/deleted
- **Zero Configuration**: Works out of the box with existing external-dns annotations

## Usage

### Automatic Publishing (Recommended)

If your service already has an `external-dns.alpha.kubernetes.io/hostname` annotation, it will be automatically published via mDNS:

```python
annotations={
    "external-dns.alpha.kubernetes.io/hostname": "prowlarr.lab"
}
```

This will publish `prowlarr.local` via mDNS.

### Explicit Publishing

To explicitly enable mDNS publishing for a service:

```python
annotations={
    "mdns.alpha.kubernetes.io/publish": "true",
    "mdns.alpha.kubernetes.io/hostname": "custom-name.local"  # Optional
}
```

### Disable Publishing

To prevent a service from being published (even if it has external-dns annotation):

```python
annotations={
    "mdns.alpha.kubernetes.io/publish": "false"
}
```

## Testing

After deployment, test mDNS resolution:

**On macOS/Linux:**
```bash
# Browse for HTTP services
dns-sd -B _http._tcp

# Resolve a specific hostname
dns-sd -G v4 prowlarr.local

# Or use dig
dig prowlarr.local
```

**On Windows:**
```powershell
# Use nslookup
nslookup prowlarr.local
```

**From within Kubernetes:**
```bash
# Install avahi-utils in a pod
kubectl run -it --rm debug --image=ubuntu:22.04 --restart=Never -- bash
apt-get update && apt-get install -y avahi-utils
avahi-resolve -n prowlarr.local
```

## Network Requirements

- mDNS uses UDP port **5353** and multicast address **224.0.0.251**
- Ensure your network allows multicast traffic
- For UniFi networks, enable mDNS in Settings > Networks
- If using VLANs, configure mDNS gateway/repeater to forward across subnets

## Troubleshooting

### Check mDNS Publisher Logs
```bash
kubectl logs -n mdns deployment/mdns-publisher -f
```

### Verify Service is Being Watched
```bash
kubectl get svc -A -o json | jq '.items[] | select(.spec.type=="LoadBalancer") | {name: .metadata.name, namespace: .metadata.namespace, annotations: .metadata.annotations}'
```

### Test mDNS Resolution
```bash
# On a client device
ping prowlarr.local
curl http://prowlarr.local
```

### Common Issues

1. **Service not published**: Check that it has LoadBalancer type and an IP assigned
2. **Can't resolve .local**: Ensure mDNS is enabled on your network/router
3. **Works on some devices but not others**: Check firewall rules for UDP 5353

## Architecture

- **Deployment**: Single replica deployment (can be scaled if needed)
- **Host Network**: Uses `hostNetwork: true` to access node's network interface
- **RBAC**: ClusterRole with read access to services
- **Library**: Uses Python `zeroconf` library for mDNS publishing

## Integration with External-DNS

This works alongside External-DNS:
- External-DNS creates DNS records in Pi-hole (`.lab` domain)
- mDNS Publisher creates mDNS records (`.local` domain)
- Both can coexist - use `.lab` for traditional DNS, `.local` for mDNS discovery

