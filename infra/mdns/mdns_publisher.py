#!/usr/bin/env python3
"""
mDNS Publisher for Kubernetes Services

Watches Kubernetes LoadBalancer services and publishes them via mDNS
so they can be discovered using .local hostnames.
"""

import os
import time
import threading
import socket
from kubernetes import client, config, watch
from zeroconf import ServiceInfo, Zeroconf

# Load Kubernetes config
try:
    config.load_incluster_config()
except:
    config.load_kube_config()

v1 = client.CoreV1Api()
zeroconf = Zeroconf()
published_services = {}


def get_hostname(service):
    """Extract hostname from service annotations or use default."""
    annotations = service.metadata.annotations or {}
    # Check for explicit mDNS hostname
    hostname = annotations.get("mdns.alpha.kubernetes.io/hostname")
    if hostname:
        # Remove domain suffix if present, keep only name
        if "." in hostname and not hostname.endswith(".local"):
            hostname = hostname.split(".")[0]
        return f"{hostname}.local"
    # Fallback to external-dns hostname
    hostname = annotations.get("external-dns.alpha.kubernetes.io/hostname")
    if hostname:
        if "." in hostname and not hostname.endswith(".local"):
            hostname = hostname.split(".")[0]
        return f"{hostname}.local"
    # Default to service name
    return f"{service.metadata.name}.local"


def should_publish(service):
    """Check if service should be published via mDNS."""
    if service.spec.type != "LoadBalancer":
        return False
    annotations = service.metadata.annotations or {}
    # Publish if explicitly requested or if external-dns hostname exists
    return (
        annotations.get("mdns.alpha.kubernetes.io/publish") == "true"
        or annotations.get("external-dns.alpha.kubernetes.io/hostname") is not None
    )


def publish_service(service):
    """Publish a service via mDNS."""
    if not should_publish(service):
        return
    
    if not service.status.load_balancer.ingress:
        return
    
    ip = service.status.load_balancer.ingress[0].ip
    if not ip:
        return
    
    hostname = get_hostname(service)
    service_key = f"{service.metadata.namespace}/{service.metadata.name}"
    
    if service_key in published_services:
        return  # Already published
    
    try:
        # Get ports
        ports = service.spec.ports or []
        http_port = None
        for port in ports:
            if port.port in [80, 443, 8080]:
                http_port = port.port
                break
        if not http_port and ports:
            http_port = ports[0].port
        
        # Publish HTTP service
        service_type = "_http._tcp.local."
        service_name = f"{service.metadata.name}._http._tcp.local."
        
        # Convert IP to bytes for zeroconf (4 bytes for IPv4)
        ip_bytes = socket.inet_aton(ip)
        
        info = ServiceInfo(
            service_type,
            service_name,
            addresses=[ip_bytes],
            port=http_port or 80,
            properties={"path": "/"},
            server=f"{hostname}.",
        )
        
        zeroconf.register_service(info)
        published_services[service_key] = (info, hostname)
        print(f"Published mDNS: {hostname} -> {ip}:{http_port}")
    except Exception as e:
        print(f"Error publishing {hostname}: {e}")


def unpublish_service(service):
    """Unpublish a service from mDNS."""
    service_key = f"{service.metadata.namespace}/{service.metadata.name}"
    if service_key in published_services:
        try:
            info, hostname = published_services[service_key]
            zeroconf.unregister_service(info)
            del published_services[service_key]
            print(f"Unpublished mDNS: {hostname}")
        except Exception as e:
            print(f"Error unpublishing {service_key}: {e}")


# Watch for services
print("Starting mDNS publisher...")
w = watch.Watch()
for event in w.stream(v1.list_service_for_all_namespaces):
    service = event["object"]
    event_type = event["type"]
    
    if event_type == "ADDED" or event_type == "MODIFIED":
        publish_service(service)
    elif event_type == "DELETED":
        unpublish_service(service)

