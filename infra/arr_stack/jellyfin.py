import pulumi
import pulumi_kubernetes as kubernetes
from pulumi_kubernetes.helm.v3 import Release, ReleaseArgs, RepositoryOptsArgs


class Jellyfin(pulumi.ComponentResource):
    def __init__(self, namespace: kubernetes.core.v1.Namespace, opts=None):
        super().__init__(
            "jellyfin",
            "jellyfin",
            None,
            opts=opts,
        )

        # Deploy Jellyfin using Helm chart
        self.release = Release(
            "jellyfin",
            ReleaseArgs(
                chart="jellyfin",
                version="2.0.0",  # Working version from utkuozdemir
                repository_opts=RepositoryOptsArgs(
                    repo="https://utkuozdemir.org/helm-charts"
                ),
                namespace=namespace.metadata.name,
                values={
                    # Service configuration
                    "service": {
                        "type": "LoadBalancer",
                        "port": 80,
                        "targetPort": 8096,  # Jellyfin container still runs on 8096
                        "loadBalancerIP": "192.168.1.40",  # Static IP for media server
                        "annotations": {
                            "metallb.universe.tf/allow-shared-ip": "jellyfin"
                        }
                    },
                    
                    # Persistence for configuration and cache
                    "persistence": {
                        "config": {
                            "enabled": True,
                            "storageClass": "longhorn",
                            "size": "10Gi",
                            "accessMode": "ReadWriteOnce"
                        },
                        "cache": {
                            "enabled": True,
                            "storageClass": "longhorn", 
                            "size": "20Gi",
                            "accessMode": "ReadWriteOnce"
                        },
                        "media": {
                            "enabled": True,
                            "existingClaim": "",  # Will need to be configured with actual media PVC
                            "subPath": ""
                        }
                    },
                    
                    # Resource limits
                    "resources": {
                        "limits": {
                            "cpu": "2000m",
                            "memory": "4Gi"
                        },
                        "requests": {
                            "cpu": "500m", 
                            "memory": "1Gi"
                        }
                    },
                    
                    # Timezone
                    "timezone": "UTC",
                    
                    # Security context - allow container to run as root for s6-supervise
                    "podSecurityContext": {
                        "runAsUser": 0,  # Run as root to fix s6-supervise permissions
                        "runAsGroup": 0,
                        "fsGroup": 1000  # Keep fsGroup for volume permissions
                    },
                    "securityContext": {
                        "allowPrivilegeEscalation": False,
                        "readOnlyRootFilesystem": False,
                        "runAsNonRoot": False  # Allow root for s6-supervise
                    },
                    
                    # Environment variables
                    "extraEnv": [
                        {
                            "name": "JELLYFIN_PublishedServerUrl",
                            "value": "http://192.168.1.40"
                        },
                        {
                            "name": "PUID",
                            "value": "1000"
                        },
                        {
                            "name": "PGID", 
                            "value": "1000"
                        }
                    ],
                    
                    # Ingress configuration (disabled by default, using LoadBalancer)
                    "ingress": {
                        "enabled": False
                    }
                },
                timeout=180,
            ),
            opts=pulumi.ResourceOptions(parent=self),
        )

        # Store references
        self.namespace = namespace
        
        # Export useful information
        self.service_ip = pulumi.Output.concat("192.168.1.40")
        self.web_url = pulumi.Output.concat("http://192.168.1.40")
