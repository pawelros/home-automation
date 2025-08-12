import pulumi
import pulumi_kubernetes as kubernetes
from pulumi_kubernetes.helm.v3 import Release, ReleaseArgs, RepositoryOptsArgs


class Loki(pulumi.ComponentResource):
    def __init__(self, opts=None):
        super().__init__(
            "loki",
            "loki",
            None,
        )

        # Create dedicated namespace for Loki
        ns = kubernetes.core.v1.Namespace(
            "loki",
            metadata=kubernetes.meta.v1.ObjectMetaArgs(
                name="loki",
            ),
        )

        # Install Loki using Helm in simple scalable deployment mode
        loki_release = Release(
            "loki",
            ReleaseArgs(
                chart="loki",
                namespace=ns.metadata.name,
                create_namespace=False,
                atomic=True,
                timeout=300,
                repository_opts=RepositoryOptsArgs(
                    repo="https://grafana.github.io/helm-charts",
                ),
                values={
                    "deploymentMode": "SimpleScalable",
                    "backend": {
                        "replicas": 2,
                        "persistence": {
                            "size": "10Gi",
                            "storageClass": "longhorn",
                        },
                        "resources": {
                            "requests": {
                                "cpu": "200m",
                                "memory": "256Mi",
                            },
                            "limits": {
                                "cpu": "1000m",
                                "memory": "2Gi",
                            },
                        },
                    },
                    "read": {
                        "replicas": 2,
                        "resources": {
                            "requests": {
                                "cpu": "100m",
                                "memory": "128Mi",
                            },
                            "limits": {
                                "cpu": "1000m",
                                "memory": "1Gi",
                            },
                        },
                    },
                    "write": {
                        "replicas": 2,
                        "persistence": {
                            "size": "10Gi",
                            "storageClass": "longhorn",
                        },
                        "resources": {
                            "requests": {
                                "cpu": "200m",
                                "memory": "256Mi",
                            },
                            "limits": {
                                "cpu": "1000m",
                                "memory": "2Gi",
                            },
                        },
                    },
                    "loki": {
                        "storage": {
                            "type": "filesystem",
                        },
                        "auth_enabled": False,
                        "commonConfig": {
                            "replication_factor": 1,
                        },
                        "limits_config": {
                            "retention_period": "1y",
                            "enforce_metric_name": False,
                            "reject_old_samples": True,
                            "reject_old_samples_max_age": "168h",  # 7 days
                            "max_cache_freshness_per_query": "10m",
                            "split_queries_by_interval": "15m",
                        },
                        "compactor": {
                            "retention_enabled": True,
                        },
                        "storage_config": {
                            "filesystem": {
                                "directory": "/var/loki/chunks",
                            },
                        },
                    },
                    "monitoring": {
                        "dashboards": {
                            "enabled": True,
                        },
                        "rules": {
                            "enabled": True,
                        },
                        "serviceMonitor": {
                            "enabled": True,
                        },
                        "selfMonitoring": {
                            "enabled": False,
                            "grafanaAgent": {
                                "installOperator": False,
                            },
                        },
                    },
                    "test": {
                        "enabled": False,
                    },
                    "gateway": {
                        "enabled": True,
                        "replicas": 1,
                        "service": {
                            "type": "LoadBalancer",
                            "port": 80,
                            "annotations": {
                                "metallb.universe.tf/loadBalancerIPs": "192.168.1.36"
                            }
                        },
                        "resources": {
                            "requests": {
                                "cpu": "100m",
                                "memory": "128Mi",
                            },
                            "limits": {
                                "cpu": "500m",
                                "memory": "512Mi",
                            },
                        },
                    },
                },
            ),
            opts=pulumi.ResourceOptions(parent=self, depends_on=[ns]),
        )

        # Export Loki gateway URL
        pulumi.export("loki_gateway_url", "http://192.168.1.36")
        pulumi.export("loki_namespace", ns.metadata.name)
