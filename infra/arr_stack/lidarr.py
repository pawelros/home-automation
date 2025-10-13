import pulumi
import pulumi_kubernetes as kubernetes
from pulumi_kubernetes.helm.v3 import Release, ReleaseArgs, RepositoryOptsArgs


class Lidarr(pulumi.ComponentResource):
    def __init__(self, namespace: kubernetes.core.v1.Namespace, opts=None):
        super().__init__(
            "lidarr",
            "lidarr",
            None,
            opts=opts,
        )

        # Deploy Lidarr using k8s-home-lab-repo chart
        self.release = Release(
            "lidarr",
            ReleaseArgs(
                chart="lidarr",
                # version="1.0.0",  # Use latest available version
                repository_opts=RepositoryOptsArgs(
                    repo="https://k8s-home-lab.github.io/helm-charts"
                ),
                namespace=namespace.metadata.name,
                values={
                    # Override the release name to get predictable service names
                    "fullnameOverride": "lidarr",
                    
                    # Image configuration
                    "image": {
                        "repository": "lscr.io/linuxserver/lidarr",
                        "tag": "version-2.13.3.4711"
                    },
                    
                    # Service configuration
                    "service": {
                        "main": {
                            "type": "LoadBalancer",
                            "loadBalancerIP": "192.168.1.47",  # Actual IP from existing deployment
                            "annotations": {
                                "metallb.universe.tf/allow-shared-ip": "lidarr"
                            },
                            "ports": {
                                "http": {
                                    "enabled": True,
                                    "port": 80,
                                    "targetPort": 8686,  # Lidarr default port
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
                            "size": "10Gi",  # Match existing PVC size
                            "accessMode": "ReadWriteOnce"
                        },
                        "media": {
                            "enabled": True,
                            "existingClaim": "arr-shared-nfs",  # Use shared NFS PVC
                            "mountPath": "/shared"  # Mount entire /mnt/SSD/arr_stack as /shared (contains media/ and downloads/)
                        }
                    },
                    
                    # Resource limits (match existing deployment)
                    "resources": {
                        "limits": {
                            "cpu": "2",  # Match existing: "2" instead of "2000m"
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
                    
                    # Probes configuration (match existing deployment)
                    "probes": {
                        "startup": {
                            "enabled": True,
                            "tcpSocket": {
                                "port": 8686
                            },
                            "failureThreshold": 30,
                            "periodSeconds": 5,
                            "successThreshold": 1,
                            "timeoutSeconds": 1
                        },
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
        self.service_ip = pulumi.Output.concat("192.168.1.47")
        self.web_url = pulumi.Output.concat("http://192.168.1.47")
        self.api_url = pulumi.Output.concat("http://192.168.1.47/api/v1")
