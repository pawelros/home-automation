from hashlib import sha256
import ipaddress
import json
from pathlib import Path
import re

import pulumi
import pulumi_kubernetes as kubernetes


class Knowledge(pulumi.ComponentResource):
    """Shared, metadata-scoped memory exposed through an authenticated MCP endpoint."""

    def __init__(self, longhorn, opts=None):
        super().__init__("custom:Knowledge", "knowledge", None, opts)
        config = pulumi.Config("knowledge")
        hostname = config.get("hostname") or "knowledge.lab"
        address = config.get("address")
        if address:
            address = str(ipaddress.IPv4Address(address))
        if not re.fullmatch(r"[a-z0-9](?:[a-z0-9.-]*[a-z0-9])?", hostname):
            raise ValueError("knowledge:hostname must be a lowercase DNS hostname")
        token = config.require_secret("token")
        directory = Path(__file__).parent
        files = {
            "Caddyfile": (directory / "Caddyfile").read_text(),
            "initialize.py": (directory / "initialize.py").read_text(),
        }
        seeds = {path.name: path.read_text() for path in (directory / "seed").glob("*.md")}
        resource_opts = pulumi.ResourceOptions(parent=self)
        namespace = kubernetes.core.v1.Namespace(
            "knowledge", metadata={"name": "knowledge"}, opts=resource_opts,
        )
        metadata = {"namespace": namespace.metadata.name}
        settings = kubernetes.core.v1.ConfigMap(
            "knowledge-settings", metadata={**metadata, "name": "knowledge-settings"},
            data=files, opts=resource_opts,
        )
        seed = kubernetes.core.v1.ConfigMap(
            "knowledge-seed", metadata={**metadata, "name": "knowledge-seed"},
            data=seeds, opts=resource_opts,
        )
        credentials = kubernetes.core.v1.Secret(
            "knowledge-auth", metadata={**metadata, "name": "knowledge-auth"},
            string_data={"token": token}, opts=resource_opts,
        )
        storage = kubernetes.core.v1.PersistentVolumeClaim(
            "knowledge-data", metadata={**metadata, "name": "knowledge-data"},
            spec={
                "accessModes": ["ReadWriteOnce"],
                "storageClassName": "longhorn",
                "resources": {"requests": {"storage": "10Gi"}},
            },
            opts=pulumi.ResourceOptions(parent=self, depends_on=[longhorn], protect=True),
        )
        image = "ghcr.io/basicmachines-co/basic-memory:0.24.1"
        security = {
            "allowPrivilegeEscalation": False,
            "capabilities": {"drop": ["ALL"]},
        }
        state_mount = {"name": "state", "mountPath": "/state"}
        settings_mount = {"name": "settings", "mountPath": "/settings", "readOnly": True}
        environment = [
            {"name": "BASIC_MEMORY_CONFIG_DIR", "value": "/state/config"},
            {"name": "BASIC_MEMORY_HOME", "value": "/state/notes/shared"},
            {"name": "BASIC_MEMORY_PROJECT_ROOT", "value": "/state/notes"},
            {"name": "BASIC_MEMORY_MCP_PROJECT", "value": "shared"},
        ]
        self.deployment = kubernetes.apps.v1.Deployment(
            "knowledge", metadata={**metadata, "name": "knowledge"},
            spec={
                "replicas": 1,
                "strategy": {"type": "Recreate"},
                "selector": {"matchLabels": {"app": "knowledge"}},
                "template": {
                    "metadata": {
                        "labels": {"app": "knowledge"},
                        "annotations": {
                            "knowledge/config-checksum": sha256(
                                json.dumps([files, seeds], sort_keys=True).encode()
                            ).hexdigest(),
                            "knowledge/token-checksum": token.apply(
                                lambda value: sha256(value.encode()).hexdigest()
                            ),
                        },
                    },
                    "spec": {
                        "automountServiceAccountToken": False,
                        "securityContext": {
                            "runAsUser": 1000, "runAsGroup": 1000,
                            "runAsNonRoot": True, "fsGroup": 1000,
                            "seccompProfile": {"type": "RuntimeDefault"},
                        },
                        "initContainers": [{
                            "name": "initialize", "image": image,
                            "command": ["python", "/settings/initialize.py"],
                            "securityContext": security,
                            "volumeMounts": [state_mount, settings_mount, {
                                "name": "seed", "mountPath": "/seed", "readOnly": True,
                            }],
                            "resources": {
                                "requests": {"cpu": "50m", "memory": "64Mi"},
                                "limits": {"cpu": "500m", "memory": "256Mi"},
                            },
                        }],
                        "containers": [{
                            "name": "memory", "image": image,
                            # Only the sidecar can reach the unauthenticated backend.
                            "command": ["basic-memory", "mcp", "--transport", "streamable-http",
                                        "--host", "127.0.0.1", "--port", "8000"],
                            "env": environment,
                            "securityContext": security,
                            "volumeMounts": [state_mount],
                            "startupProbe": {
                                "exec": {"command": ["python", "-c",
                                    "import socket; socket.create_connection(('127.0.0.1', 8000), 2).close()"]},
                                "periodSeconds": 10, "failureThreshold": 90,
                            },
                            "readinessProbe": {
                                "exec": {"command": ["python", "-c",
                                    "import socket; socket.create_connection(('127.0.0.1', 8000), 2).close()"]},
                                "periodSeconds": 15,
                            },
                            "resources": {
                                "requests": {"cpu": "100m", "memory": "512Mi"},
                                "limits": {"cpu": "2000m", "memory": "2Gi"},
                            },
                        }, {
                            "name": "gateway", "image": "caddy:2.10.2-alpine",
                            "command": ["caddy", "run", "--config", "/settings/Caddyfile",
                                        "--adapter", "caddyfile"],
                            "securityContext": {
                                **security,
                                # The official binary carries this file capability;
                                # excluding it from the bounding set prevents exec.
                                "capabilities": {"drop": ["ALL"], "add": ["NET_BIND_SERVICE"]},
                            },
                            "env": [
                                {"name": "KNOWLEDGE_DEFAULT_SNI", "value": address or hostname},
                                {"name": "KNOWLEDGE_SITES", "value": ", ".join(
                                    "https://" + host + ":8443"
                                    for host in [hostname] + ([address] if address else [])
                                )},
                                {"name": "KNOWLEDGE_TOKEN", "valueFrom": {"secretKeyRef": {
                                    "name": credentials.metadata.name, "key": "token",
                                }}},
                                {"name": "XDG_DATA_HOME", "value": "/state/caddy/data"},
                                {"name": "XDG_CONFIG_HOME", "value": "/state/caddy/config"},
                            ],
                            "ports": [{"name": "https", "containerPort": 8443}],
                            "volumeMounts": [state_mount, settings_mount],
                            "readinessProbe": {"httpGet": {"path": "/healthz", "port": 8081}},
                            "livenessProbe": {"httpGet": {"path": "/healthz", "port": 8081}},
                            "resources": {
                                "requests": {"cpu": "25m", "memory": "32Mi"},
                                "limits": {"cpu": "500m", "memory": "128Mi"},
                            },
                        }],
                        "volumes": [
                            {"name": "state", "persistentVolumeClaim": {"claimName": storage.metadata.name}},
                            {"name": "settings", "configMap": {"name": settings.metadata.name}},
                            {"name": "seed", "configMap": {"name": seed.metadata.name}},
                        ],
                    },
                },
            },
            opts=pulumi.ResourceOptions(parent=self, depends_on=[credentials]),
        )
        self.service = kubernetes.core.v1.Service(
            "knowledge", metadata={**metadata, "name": "knowledge", "annotations": {
                "external-dns.alpha.kubernetes.io/hostname": hostname,
            }},
            spec={
                "type": "LoadBalancer", "selector": {"app": "knowledge"},
                **({"loadBalancerIP": address} if address else {}),
                "ports": [{"name": "https", "port": 443, "targetPort": 8443}],
            }, opts=resource_opts,
        )
        self.url = "https://" + hostname + "/mcp"
        self.register_outputs({"url": self.url})
