import pulumi
import pulumi_kubernetes as kubernetes
from pulumi_kubernetes.helm.v3 import Release, ReleaseArgs, RepositoryOptsArgs


class K8sMonitoring(pulumi.ComponentResource):
    def __init__(self, loki_url: str, mimir_url: str, opts=None):
        super().__init__(
            "k8s-monitoring",
            "k8s-monitoring",
            None,
            opts=opts,
        )

        # Create monitoring namespace
        monitoring_ns = kubernetes.core.v1.Namespace(
            "monitoring",
            metadata=kubernetes.meta.v1.ObjectMetaArgs(
                name="monitoring",
            ),
            opts=pulumi.ResourceOptions(parent=self),
        )

        # Install Grafana Kubernetes Monitoring Helm chart
        k8s_monitoring_release = Release(
            "k8s-monitoring",
            ReleaseArgs(
                chart="k8s-monitoring",
                version="1.4.4",  # Use version 1.x as suggested
                namespace=monitoring_ns.metadata.name,
                create_namespace=False,
                atomic=True,
                timeout=180,
                repository_opts=RepositoryOptsArgs(
                    repo="https://grafana.github.io/helm-charts",
                ),
                values={
                    # Cluster configuration
                    "cluster": {
                        "name": "home-automation",
                        "platform": "",  # Must be "" or "openshift"
                    },
                    
                    # External services configuration
                    "externalServices": {
                        "loki": {
                            "host": loki_url,
                            "basicAuth": {
                                "username": "",
                                "password": "",
                            },
                            "tls": {
                                "insecure_skip_verify": True,
                            },
                        },
                        "prometheus": {
                            "host": mimir_url,
                            "writeEndpoint": "/api/v1/push",  # Try to override the default path
                            "basicAuth": {
                                "username": "",
                                "password": "",
                            },
                            "tls": {
                                "insecure_skip_verify": True,
                            },
                        },
                    },
                    
                    # Metrics collection configuration
                    "metrics": {
                        "enabled": True,
                        "cost": {
                            "enabled": True,
                        },
                        "node-exporter": {
                            "enabled": True,
                        },
                        "kube-state-metrics": {
                            "enabled": True,
                        },
                        "apiserver": {
                            "enabled": True,
                        },
                        "kubelet": {
                            "enabled": True,
                        },
                        "cadvisor": {
                            "enabled": True,
                        },
                        "kubeControllerManager": {
                            "enabled": False,  # Usually not accessible in managed clusters
                        },
                        "kubeProxy": {
                            "enabled": False,  # Usually not accessible in managed clusters
                        },
                        "kubeScheduler": {
                            "enabled": False,  # Usually not accessible in managed clusters
                        },
                        "kubeEtcd": {
                            "enabled": False,  # Usually not accessible in managed clusters
                        },
                    },
                    
                    # Logs collection configuration
                    "logs": {
                        "enabled": True,
                        "pod_logs": {
                            "enabled": True,
                            "annotation_selector": "",  # Collect all pod logs
                            "label_selector": "",
                        },
                        "cluster_events": {
                            "enabled": True,
                        },
                    },
                    
                    # Traces configuration (optional)
                    "traces": {
                        "enabled": False,  # Disable for now, can enable later if needed
                    },
                    
                    # Profiles configuration (optional)
                    "profiles": {
                        "enabled": False,  # Disable for now
                    },
                    
                    # Receivers configuration
                    "receivers": {
                        "grpc": {
                            "enabled": False,
                        },
                        "http": {
                            "enabled": False,
                        },
                        "zipkin": {
                            "enabled": False,
                        },
                    },
                    
                    # OpenCost for cost monitoring (disabled for now due to auth issues)
                    "opencost": {
                        "enabled": False,
                    },
                    
                    # Kepler for energy monitoring (optional)
                    "kepler": {
                        "enabled": False,  # Can enable if you want energy metrics
                    },
                    
                    # Alloy configuration for telemetry collection
                    "alloy": {
                        "enabled": True,
                        "alloy": {
                            "resources": {
                                "requests": {
                                    "cpu": "200m", 
                                    "memory": "512Mi",
                                },
                                "limits": {
                                    "cpu": "800m",
                                    "memory": "1Gi",
                                },
                            },
                            "logging": {
                                "level": "info",
                            },
                        },
                    },
                    
                    # Disable ServiceMonitor since we don't have Prometheus Operator
                    "serviceMonitor": {
                        "enabled": False,
                    },
                    
                    # Disable Prometheus Operator objects since we don't have the operator
                    "prometheusOperatorObjects": {
                        "enabled": False,
                    },
                    
                    # Disable CRD installation completely
                    "prometheus-operator-crds": {
                        "enabled": False,
                    },
                    
                    # Test configuration
                    "test": {
                        "enabled": False,
                    },
                },
            ),
            opts=pulumi.ResourceOptions(parent=self),
        )

        # Store references
        self.release = k8s_monitoring_release
        self.namespace = monitoring_ns

        # Export useful information
        pulumi.export("k8s_monitoring_namespace", monitoring_ns.metadata.name)
        pulumi.export("k8s_monitoring_chart_status", k8s_monitoring_release.status)
