import pulumi
import pulumi_kubernetes as kubernetes
from pulumi_kubernetes.helm.v3 import Release, ReleaseArgs, RepositoryOptsArgs


class Loki(pulumi.ComponentResource):
    def __init__(self, object_storage, opts=None):
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
                version="6.44.0",  # Pin to specific version to prevent auto-upgrades
                namespace=ns.metadata.name,
                create_namespace=False,
                atomic=True,
                timeout=300,
                repository_opts=RepositoryOptsArgs(
                    repo="https://grafana.github.io/helm-charts",
                ),
                values={
                    "deploymentMode": "SimpleScalable",
                    "fullnameOverride": "loki",
                    "backend": {
                        "replicas": 2,
                        "persistence": {
                            "size": "2Gi",
                            "storageClass": "longhorn-monitoring",
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
                            "size": "2Gi",
                            "storageClass": "longhorn-monitoring",
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
                                "endpoint": "http://" + object_storage.endpoint,
                                "region": "us-east-1",
                                "accessKeyId": object_storage.access_key,
                                "secretAccessKey": object_storage.secret_key,
                                "s3ForcePathStyle": True,
                                "insecure": True,
                            },
                        },
                        "auth_enabled": False,
                        "commonConfig": {
                            "replication_factor": 1,
                        },
                        "limits_config": {
                            "retention_period": "168h",
                            "reject_old_samples": True,
                            "reject_old_samples_max_age": "168h",  # 7 days
                            "max_cache_freshness_per_query": "10m",
                            "split_queries_by_interval": "15m",
                        },
                        "compactor": {
                            "retention_enabled": True,
                            "delete_request_store": "s3",
                            "working_directory": "/var/loki/compactor",
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
                        "storage_config": {
                            "tsdb_shipper": {
                                "active_index_directory": "/var/loki/tsdb-index",
                                "cache_location": "/var/loki/tsdb-cache",
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
            opts=pulumi.ResourceOptions(parent=self, depends_on=[ns, object_storage.ready]),
        )

        # Export Loki gateway URL
        pulumi.export("loki_gateway_url", "http://192.168.1.36")
        pulumi.export("loki_namespace", ns.metadata.name)
