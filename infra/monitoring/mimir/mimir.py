import pulumi
import pulumi_kubernetes as kubernetes
from pulumi_kubernetes.helm.v3 import Release, ReleaseArgs, RepositoryOptsArgs


class Mimir(pulumi.ComponentResource):
    def __init__(self, minio=None, opts=None):
        super().__init__(
            "mimir",
            "mimir",
            None,
        )

        # Create dedicated namespace for Mimir
        ns = kubernetes.core.v1.Namespace(
            "mimir",
            metadata=kubernetes.meta.v1.ObjectMetaArgs(
                name="mimir",
            ),
        )

        # Install Mimir using Helm
        mimir_release = Release(
            "mimir",
            ReleaseArgs(
                chart="mimir-distributed",
                version="5.4.0",
                namespace=ns.metadata.name,
                create_namespace=False,
                atomic=True,
                timeout=120,
                repository_opts=RepositoryOptsArgs(
                    repo="https://grafana.github.io/helm-charts",
                ),
                values={
                    "fullnameOverride": "mimir",
                    
                    # Disable internal MinIO since we use external MinIO
                    "minio": {
                        "enabled": False,
                    },
                    # Mimir configuration
                    "mimir": {
                        "structuredConfig": {
                            "common": {
                                "storage": {
                                    "backend": "s3",
                                    "s3": {
                                        "endpoint": "minio.minio.svc.cluster.local:9000",
                                        "region": "us-east-1",
                                        "access_key_id": "minio",
                                        "secret_access_key": "minio123",
                                        "insecure": True,
                                        "bucket_name": "mimir-blocks",
                                    },
                                },
                            },
                            "limits": {
                                "compactor_blocks_retention_period": "1y",
                            },
                        },
                    },
                    
                    # Global storage configuration (alternative approach)
                    "global": {
                        "extraEnv": [
                            {
                                "name": "MIMIR_COMMON_STORAGE_BACKEND",
                                "value": "s3",
                            },
                            {
                                "name": "MIMIR_COMMON_STORAGE_S3_ENDPOINT",
                                "value": "minio.minio.svc.cluster.local:9000",
                            },
                            {
                                "name": "MIMIR_COMMON_STORAGE_S3_REGION",
                                "value": "us-east-1",
                            },
                            {
                                "name": "MIMIR_COMMON_STORAGE_S3_ACCESS_KEY_ID",
                                "value": "minio",
                            },
                            {
                                "name": "MIMIR_COMMON_STORAGE_S3_SECRET_ACCESS_KEY",
                                "value": "minio123",
                            },
                            {
                                "name": "MIMIR_COMMON_STORAGE_S3_BUCKET_NAME",
                                "value": "mimir-blocks",
                            },
                            {
                                "name": "MIMIR_COMMON_STORAGE_S3_INSECURE",
                                "value": "true",
                            },
                        ],
                    },
                    "compactor": {
                        "replicas": 1,
                        "resources": {
                            "requests": {
                                "cpu": "100m",
                                "memory": "256Mi",
                            },
                            "limits": {
                                "cpu": "1000m",
                                "memory": "1Gi",
                            },
                        },
                    },
                    "distributor": {
                        "replicas": 1,
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
                    "ingester": {
                        "replicas": 1,
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
                        "zoneAwareReplication": {
                            "enabled": False,
                        },
                    },
                    "querier": {
                        "replicas": 1,
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
                    "query_frontend": {
                        "replicas": 1,
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
                    "store_gateway": {
                        "replicas": 1,
                        "resources": {
                            "requests": {
                                "cpu": "100m",
                                "memory": "256Mi",
                            },
                            "limits": {
                                "cpu": "500m",
                                "memory": "1Gi",
                            },
                        },
                        "zoneAwareReplication": {
                            "enabled": False,
                        },
                    },
                    "nginx": {
                        "enabled": True,
                        "replicas": 1,
                        "service": {
                            "type": "LoadBalancer",
                            "annotations": {
                                "metallb.universe.tf/loadBalancerIPs": "192.168.1.39"
                            }
                        },
                        "resources": {
                            "requests": {
                                "cpu": "50m",
                                "memory": "64Mi",
                            },
                            "limits": {
                                "cpu": "200m",
                                "memory": "256Mi",
                            },
                        },
                    },
                    "ruler": {
                        "enabled": False,  # Disable ruler for now
                    },
                    "alertmanager": {
                        "enabled": False,  # Disable alertmanager for now
                    },
                },
            ),
            opts=pulumi.ResourceOptions(parent=self, depends_on=[ns] + ([minio] if minio else [])),
        )

        # Export Mimir info
        pulumi.export("mimir_endpoint", "http://192.168.1.39")
        pulumi.export("mimir_namespace", ns.metadata.name)
        pulumi.export("mimir_query_url", "http://192.168.1.39/prometheus")
