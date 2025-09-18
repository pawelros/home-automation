import pulumi
import pulumi_kubernetes as kubernetes
from pulumi_kubernetes.helm.v3 import Release, ReleaseArgs, RepositoryOptsArgs


class FlareSolverr(pulumi.ComponentResource):
    def __init__(self, namespace: kubernetes.core.v1.Namespace, opts=None):
        super().__init__(
            "flaresolverr",
            "flaresolverr",
            None,
            opts=opts,
        )

        # Deploy FlareSolverr using k8s-home-lab-repo chart
        self.release = Release(
            "flaresolverr",
            ReleaseArgs(
                chart="flaresolverr",
                # version="1.0.0",  # Use latest available version
                repository_opts=RepositoryOptsArgs(
                    repo="https://k8s-home-lab.github.io/helm-charts"
                ),
                namespace=namespace.metadata.name,
                values={
                    # Override the release name to get predictable service names
                    "fullnameOverride": "flaresolverr",
                    
                    # Image configuration
                    "image": {
                        "repository": "ghcr.io/flaresolverr/flaresolverr",
                        "tag": "latest"
                    },
                    
                    # Service configuration
                    "service": {
                        "main": {
                            "type": "ClusterIP",  # Internal service only, Prowlarr will connect internally
                            "ports": {
                                "http": {
                                    "enabled": True,
                                    "port": 8191,
                                    "targetPort": 8191,
                                    "protocol": "TCP"
                                }
                            }
                        }
                    },
                    
                    # Environment variables
                    "env": {
                        "LOG_LEVEL": "info",
                        "LOG_HTML": "false",
                        "CAPTCHA_SOLVER": "none",
                        "TZ": "UTC"
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
                    
                    # Security context
                    "securityContext": {
                        "runAsUser": 1000,
                        "runAsGroup": 1000,
                        "fsGroup": 1000,
                        "runAsNonRoot": True,
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
                                    "port": 8191
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
                                    "port": 8191
                                },
                                "initialDelaySeconds": 30,
                                "periodSeconds": 30,
                                "timeoutSeconds": 10,
                                "failureThreshold": 5
                            }
                        }
                    },
                    
                    # No persistence needed for FlareSolverr
                    "persistence": {},
                    
                    # Ingress configuration (disabled, internal service only)
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
        self.service_name = pulumi.Output.concat("flaresolverr")
        self.internal_url = pulumi.Output.concat("http://flaresolverr.arr-stack.svc.cluster.local:8191")
        self.api_url = pulumi.Output.concat("http://flaresolverr.arr-stack.svc.cluster.local:8191/v1")
