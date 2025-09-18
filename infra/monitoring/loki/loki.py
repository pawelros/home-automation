import pulumi
import pulumi_kubernetes as kubernetes
from pulumi_kubernetes.helm.v3 import Release, ReleaseArgs, RepositoryOptsArgs


class Loki(pulumi.ComponentResource):
    def __init__(self, minio=None, opts=None):
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
                timeout=180,
                repository_opts=RepositoryOptsArgs(
                    repo="https://grafana.github.io/helm-charts",
                ),
                values={
                    "deploymentMode": "SimpleScalable",
                    "fullnameOverride": "loki",
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
                            "type": "s3",
                            "bucketNames": {
                                "chunks": "loki-chunks",
                                "ruler": "loki-ruler", 
                                "admin": "loki-admin",
                            },
                            "s3": {
                                "endpoint": "http://minio.minio.svc.cluster.local:9000",
                                "region": "us-east-1",
                                "accessKeyId": "minio",
                                "secretAccessKey": "minio123",
                                "s3ForcePathStyle": True,
                                "insecure": True,
                            },
                        },
                        "auth_enabled": False,
                        "commonConfig": {
                            "replication_factor": 1,
                        },
                        "limitsConfig": {
                            "retention_period": "1y",
                            "enforce_metric_name": False,
                            "reject_old_samples": True,
                            "reject_old_samples_max_age": "168h",  # 7 days
                            "max_cache_freshness_per_query": "10m",
                            "split_queries_by_interval": "15m",
                        },
                        "compactor": {
                            "retention_enabled": True,
                            "delete_request_store": "s3",
                        },
                        "schemaConfig": {
                            "configs": [
                                {
                                    "from": "2024-01-01",
                                    "store": "tsdb",
                                    "object_store": "s3",
                                    "schema": "v13",
                                    "index": {
                                        "prefix": "loki_index_",
                                        "period": "24h",
                                    },
                                }
                            ]
                        },
                        "storageConfig": {
                            "tsdb_shipper": {
                                "active_index_directory": "/var/loki/tsdb-index",
                                "cache_location": "/var/loki/tsdb-cache",
                            },
                            "delete_store": {
                                "store": "s3",
                            },
                        },
                    },
                    # Configure chunks-cache (memcached) to use only 0.5GB instead of default 8GB
                    "chunksCache": {
                        "enabled": True,
                        "allocatedMemory": 512,  # 0.5GB in MB
                        "resources": {
                            "requests": {
                                "cpu": "50m",
                                "memory": "619Mi",  # floor((512 * 12 + 5) / 10) = 619Mi (20% headroom + 5Mi)
                            },
                            "limits": {
                                "cpu": "200m", 
                                "memory": "619Mi",  # Same limit to ensure predictable memory usage
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
                        "enabled": True,
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
            opts=pulumi.ResourceOptions(parent=self, depends_on=[ns] + ([minio] if minio else [])),
        )

        # Export Loki gateway URL
        pulumi.export("loki_gateway_url", "http://192.168.1.36")
        pulumi.export("loki_namespace", ns.metadata.name)
