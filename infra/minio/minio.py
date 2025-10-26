import pulumi
import pulumi_kubernetes as kubernetes
from pulumi_kubernetes.helm.v3 import Release, ReleaseArgs, RepositoryOptsArgs


class MinIO(pulumi.ComponentResource):
    def __init__(self, opts=None):
        super().__init__(
            "minio",
            "minio",
            None,
        )

        # Create dedicated namespace for MinIO
        ns = kubernetes.core.v1.Namespace(
            "minio",
            metadata=kubernetes.meta.v1.ObjectMetaArgs(
                name="minio",
            ),
        )

        # Install MinIO using Helm
        minio_release = Release(
            "minio",
            ReleaseArgs(
                chart="minio",
                version="5.4.0",
                namespace=ns.metadata.name,
                create_namespace=False,
                atomic=True,
                timeout=300,
                repository_opts=RepositoryOptsArgs(
                    repo="https://charts.min.io/",
                ),
                values={
                    "mode": "standalone",
                    "rootUser": "minio",
                    "rootPassword": "minio123",
                    "fullnameOverride": "minio",
                    "image": {
                        "tag": "RELEASE.2024-12-18T13-15-44Z"
                    },
                    "persistence": {
                        "enabled": True,
                        "size": "10Gi",
                        "storageClass": "longhorn",
                    },
                    "service": {
                        "type": "LoadBalancer",
                        "port": 9000,
                        "annotations": {
                            "metallb.universe.tf/loadBalancerIPs": "192.168.1.37"
                        }
                    },
                    "serviceAccount": {
                        "create": True,
                    },
                    "consoleService": {
                        "type": "LoadBalancer",
                        "port": 9001,
                        "annotations": {
                            "metallb.universe.tf/loadBalancerIPs": "192.168.1.38"
                        }
                    },
                    "resources": {
                        "requests": {
                            "cpu": "100m",
                            "memory": "128Mi",
                        },
                        "limits": {
                            "cpu": "1000m",
                            "memory": "2Gi",
                        },
                    },
                    "buckets": [
                        {
                            "name": "loki-chunks",
                            "policy": "none",
                            "purge": False,
                        },
                        {
                            "name": "loki-ruler",
                            "policy": "none", 
                            "purge": False,
                        },
                        {
                            "name": "loki-admin",
                            "policy": "none",
                            "purge": False,
                        },
                        {
                            "name": "mimir-blocks",
                            "policy": "none",
                            "purge": False,
                        },
                        {
                            "name": "mimir-alertmanager",
                            "policy": "none",
                            "purge": False,
                        },
                        {
                            "name": "mimir-ruler",
                            "policy": "none",
                            "purge": False,
                        },
                    ],
                },
            ),
            opts=pulumi.ResourceOptions(parent=self, depends_on=[ns]),
        )

        # Export MinIO access info
        pulumi.export("minio_endpoint", "http://192.168.1.37:9000")
        pulumi.export("minio_console", "http://192.168.1.38:9001")
        pulumi.export("minio_access_key", "minio")
        pulumi.export("minio_secret_key", "minio123")
        pulumi.export("minio_namespace", ns.metadata.name)
