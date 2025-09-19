import pulumi
import pulumi_kubernetes as kubernetes
from pulumi_kubernetes.helm.v3 import Release, ReleaseArgs, RepositoryOptsArgs


class Bazarr(pulumi.ComponentResource):
    def __init__(self, namespace: kubernetes.core.v1.Namespace, opts=None):
        super().__init__(
            "bazarr",
            "bazarr",
            None,
            opts=opts,
        )

        # Deploy Bazarr using k8s-home-lab-repo chart
        self.release = Release(
            "bazarr",
            ReleaseArgs(
                chart="bazarr",
                # version="1.0.0",  # Use latest available version
                repository_opts=RepositoryOptsArgs(
                    repo="https://k8s-home-lab.github.io/helm-charts"
                ),
                namespace=namespace.metadata.name,
                values={
                    # Override the release name to get predictable service names
                    "fullnameOverride": "bazarr",
                    
                    # Global configuration to fix chart template issues
                    "global": {
                        "labels": {}
                    },
                    
                    # Image configuration
                    "image": {
                        "repository": "lscr.io/linuxserver/bazarr",
                        "tag": "1.4.3"
                    },
                    
                    # Service configuration
                    "service": {
                        "main": {
                            "type": "LoadBalancer",
                            "loadBalancerIP": "192.168.1.45",  # Static IP for Bazarr
                            "annotations": {
                                "metallb.universe.tf/allow-shared-ip": "bazarr"
                            },
                            "ports": {
                                "http": {
                                    "enabled": True,
                                    "port": 80,
                                    "targetPort": 6767,  # Bazarr default port
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
                    
                    # Persistence for configuration and media access
                    "persistence": {
                        "config": {
                            "enabled": True,
                            "storageClass": "longhorn",
                            "size": "5Gi",  # Config storage
                            "accessMode": "ReadWriteOnce"
                        },
                        "media": {
                            "enabled": True,
                            "existingClaim": "arr-media-shared-ssd",  # Use shared SSD media PVC
                            "mountPath": "/media"  # Mount entire shared media for subtitle access
                        }
                    },
                    
                    # Resource limits
                    "resources": {
                        "limits": {
                            "cpu": "1000m",
                            "memory": "1Gi"
                        },
                        "requests": {
                            "cpu": "100m", 
                            "memory": "256Mi"
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
                    
                    # Node affinity to ensure pod runs on k8s-node-1 where SSD is located
                    "nodeSelector": {
                        "kubernetes.io/hostname": "k8s-node-1"
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
        self.service_ip = pulumi.Output.concat("192.168.1.45")
        self.web_url = pulumi.Output.concat("http://192.168.1.45")
        self.api_url = pulumi.Output.concat("http://192.168.1.45/api")

