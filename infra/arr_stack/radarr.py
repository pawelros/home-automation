import pulumi
import pulumi_kubernetes as kubernetes
from pulumi_kubernetes.helm.v3 import Release, ReleaseArgs, RepositoryOptsArgs


class Radarr(pulumi.ComponentResource):
    def __init__(self, namespace: kubernetes.core.v1.Namespace, opts=None):
        super().__init__(
            "radarr",
            "radarr",
            None,
            opts=opts,
        )

        # Deploy Radarr using k8s-home-lab-repo chart
        self.release = Release(
            "radarr",
            ReleaseArgs(
                chart="radarr",
                # version="1.0.0",  # Use latest available version
                repository_opts=RepositoryOptsArgs(
                    repo="https://k8s-home-lab.github.io/helm-charts"
                ),
                namespace=namespace.metadata.name,
                values={
                    # Override the release name to get predictable service names
                    "fullnameOverride": "radarr",
                    
                    # Image configuration
                    "image": {
                        "repository": "lscr.io/linuxserver/radarr",
                        "tag": "5.14.0"
                    },
                    
                    # Service configuration
                    "service": {
                        "main": {
                            "type": "LoadBalancer",
                            "loadBalancerIP": "192.168.1.46",  # Static IP for Radarr
                            "annotations": {
                                "metallb.universe.tf/allow-shared-ip": "radarr"
                            },
                            "ports": {
                                "http": {
                                    "enabled": True,
                                    "port": 80,
                                    "targetPort": 7878,  # Radarr default port
                                    "protocol": "TCP"
                                }
                            }
                        }
                    },
                    
                    # Environment variables
                    "env": {
                        "TZ": "UTC",
                        "PUID": "568",  # LinuxServer.io will handle user switching
                        "PGID": "568"
                    },
                    
                    # Persistence for configuration and shared NFS storage
                    "persistence": {
                        "config": {
                            "enabled": True,
                            "storageClass": "longhorn",
                            "size": "10Gi",  # Can't reduce existing PVC size, but it's still way more than needed
                            "accessMode": "ReadWriteOnce"
                        },
                        "media": {
                            "enabled": True,
                            "existingClaim": "arr-shared-nfs",  # Use shared NFS PVC
                            "mountPath": "/shared"  # Mount entire /mnt/SSD as /shared (contains media/ and downloads/)
                        }
                    },
                    
                    # Resource limits
                    "resources": {
                        "limits": {
                            "cpu": "2000m",
                            "memory": "2Gi"
                        },
                        "requests": {
                            "cpu": "200m", 
                            "memory": "512Mi"
                        }
                    },
                    
                    # Security context - force volume ownership with fsGroupChangePolicy
                    "securityContext": {
                        "runAsUser": 0,  # LinuxServer.io containers need root for s6-overlay
                        "runAsGroup": 0,
                        "fsGroup": 568,  # Volume group ownership for PUID/PGID
                        "fsGroupChangePolicy": "Always",  # Force ownership change on every mount
                        "runAsNonRoot": False,
                        "allowPrivilegeEscalation": False,
                        "readOnlyRootFilesystem": False
                    },
                    
                    # Probes configuration (simplified to avoid conflicts)
                    "probes": {
                        "liveness": {
                            "enabled": False  # Disable to avoid chart conflicts
                        },
                        "readiness": {
                            "enabled": False  # Disable to avoid chart conflicts
                        }
                    },
                    
                    # Ingress configuration (disabled, using LoadBalancer)
                    "ingress": {
                        "main": {
                            "enabled": False
                        }
                    }
                },
                timeout=180,
            ),
            opts=pulumi.ResourceOptions(parent=self),
        )

        # Store references
        self.namespace = namespace
        
        # Export useful information
        self.service_ip = pulumi.Output.concat("192.168.1.46")
        self.web_url = pulumi.Output.concat("http://192.168.1.46")
        self.api_url = pulumi.Output.concat("http://192.168.1.46/api/v3")
