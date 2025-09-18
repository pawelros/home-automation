import pulumi
import pulumi_kubernetes as kubernetes
from pulumi_kubernetes.helm.v3 import Release, ReleaseArgs, RepositoryOptsArgs


class Prowlarr(pulumi.ComponentResource):
    def __init__(self, namespace: kubernetes.core.v1.Namespace, opts=None):
        super().__init__(
            "prowlarr",
            "prowlarr",
            None,
            opts=opts,
        )

        # Deploy Prowlarr using k8s-home-lab-repo chart
        self.release = Release(
            "prowlarr",
            ReleaseArgs(
                chart="prowlarr",
                # version="1.0.0",  # Use latest available version
                repository_opts=RepositoryOptsArgs(
                    repo="https://k8s-home-lab.github.io/helm-charts"
                ),
                namespace=namespace.metadata.name,
                values={
                    # Override the release name to get predictable service names
                    "fullnameOverride": "prowlarr",
                    
                    # Image configuration
                    "image": {
                        "repository": "lscr.io/linuxserver/prowlarr",
                        "tag": "1.21.2"
                    },
                    
                    # Service configuration
                    "service": {
                        "main": {
                            "type": "LoadBalancer",
                            "loadBalancerIP": "192.168.1.41",
                            "annotations": {
                                "metallb.universe.tf/allow-shared-ip": "prowlarr"
                            },
                            "ports": {
                                "http": {
                                    "enabled": True,
                                    "port": 80,
                                    "targetPort": 9696,
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
                    
                    # Persistence for configuration
                    "persistence": {
                        "config": {
                            "enabled": True,
                            "storageClass": "longhorn",
                            "size": "5Gi",
                            "accessMode": "ReadWriteOnce"
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
                        "runAsUser": 0,  # Run as root to fix s6-supervise permissions
                        "runAsGroup": 0,
                        "fsGroup": 568,  # Keep fsGroup for volume permissions
                        "fsGroupChangePolicy": "Always",  # Force ownership change on every mount
                        "runAsNonRoot": False,
                        "allowPrivilegeEscalation": False,
                        "readOnlyRootFilesystem": False
                    },
                    
                    # Probes configuration
                    "probes": {
                        "liveness": {
                            "enabled": True,
                            "custom": True,
                            "spec": {
                                "httpGet": {
                                    "path": "/",
                                    "port": 9696
                                },
                                "initialDelaySeconds": 30,
                                "periodSeconds": 30,
                                "timeoutSeconds": 10,
                                "failureThreshold": 5
                            }
                        },
                        "readiness": {
                            "enabled": True,
                            "custom": True,
                            "spec": {
                                "httpGet": {
                                    "path": "/",
                                    "port": 9696
                                },
                                "initialDelaySeconds": 30,
                                "periodSeconds": 30,
                                "timeoutSeconds": 10,
                                "failureThreshold": 5
                            }
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
        self.service_ip = pulumi.Output.concat("192.168.1.41")
        self.web_url = pulumi.Output.concat("http://192.168.1.41")
        self.api_url = pulumi.Output.concat("http://192.168.1.41/api")
