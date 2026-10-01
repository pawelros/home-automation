import pulumi
import pulumi_kubernetes as kubernetes
from pulumi_kubernetes.helm.v3 import Release, ReleaseArgs, RepositoryOptsArgs


BUCKETS = (
    "loki-chunks", "loki-ruler", "loki-admin",
    "mimir-blocks", "mimir-alertmanager", "mimir-ruler",
)


class RustFS(pulumi.ComponentResource):
    def __init__(self, longhorn, opts=None):
        super().__init__("rustfs", "rustfs", None, opts)

        self.endpoint = "rustfs-svc.rustfs.svc.cluster.local:9000"
        self.access_key = "monitoring-storage"
        self.secret_key = pulumi.Config().require_secret("object-storage-secret-key")
        ns = kubernetes.core.v1.Namespace(
            "rustfs", metadata={"name": "rustfs"},
            opts=pulumi.ResourceOptions(parent=self),
        )
        credentials = kubernetes.core.v1.Secret(
            "rustfs-credentials",
            metadata={"name": "rustfs-credentials", "namespace": ns.metadata.name},
            string_data={
                "RUSTFS_ACCESS_KEY": self.access_key,
                "RUSTFS_SECRET_KEY": self.secret_key,
            },
            opts=pulumi.ResourceOptions(parent=self),
        )
        data = kubernetes.core.v1.PersistentVolumeClaim(
            "rustfs-data",
            metadata={"name": "rustfs-data", "namespace": ns.metadata.name},
            spec={
                "accessModes": ["ReadWriteOnce"],
                "storageClassName": longhorn.monitoring_storage_class.metadata.name,
                "resources": {"requests": {"storage": "30Gi"}},
            },
            opts=pulumi.ResourceOptions(parent=self),
        )
        self.release = Release(
            "rustfs",
            ReleaseArgs(
                name="rustfs", chart="rustfs", version="1.0.0",
                namespace=ns.metadata.name,
                repository_opts=RepositoryOptsArgs(repo="https://charts.rustfs.com"),
                atomic=True, timeout=600,
                values={
                    "fullnameOverride": "rustfs",
                    "mode": {
                        "standalone": {"enabled": True, "existingClaim": {"dataClaim": "rustfs-data"}},
                        "distributed": {"enabled": False},
                    },
                    "image": {
                        "rustfs": {"tag": "1.0.0"},
                        "initImage": {"tag": "1.37.0"},
                    },
                    "secret": {"existingSecret": "rustfs-credentials"},
                    "config": {"rustfs": {"obs_log_directory": ""}},
                    "resources": {
                        "requests": {"cpu": "200m", "memory": "512Mi"},
                        "limits": {"cpu": "2000m", "memory": "4Gi"},
                    },
                    "extraVolumes": [{"name": "tmp", "emptyDir": {}}],
                    "extraVolumeMounts": [{"name": "tmp", "mountPath": "/tmp"}],
                },
            ),
            opts=pulumi.ResourceOptions(parent=self, depends_on=[credentials, data]),
        )
        for name, address, port in [("rustfs-api", "192.168.1.37", 9000), ("rustfs-console", "192.168.1.38", 9001)]:
            kubernetes.core.v1.Service(
                name,
                metadata={
                    "name": name, "namespace": ns.metadata.name,
                    "annotations": {"metallb.universe.tf/loadBalancerIPs": address},
                },
                spec={
                    "type": "LoadBalancer",
                    "selector": {"app.kubernetes.io/name": "rustfs", "app.kubernetes.io/instance": "rustfs"},
                    "ports": [{"name": name, "port": port, "targetPort": port}],
                },
                opts=pulumi.ResourceOptions(parent=self, depends_on=[self.release]),
            )

        # Idempotent provisioning; consumers wait until all six buckets exist.
        script = """set -eu
for bucket in """ + " ".join(BUCKETS) + """; do
    if ! aws --endpoint-url "$S3_ENDPOINT" s3api head-bucket --bucket "$bucket" >/dev/null 2>&1; then
        aws --endpoint-url "$S3_ENDPOINT" s3api create-bucket --bucket "$bucket" >/dev/null
    fi
done
"""
        self.ready = kubernetes.batch.v1.Job(
            "rustfs-buckets",
            metadata={"name": "rustfs-buckets", "namespace": ns.metadata.name},
            spec={
                "backoffLimit": 3,
                "activeDeadlineSeconds": 300,
                "template": {"spec": {
                    "restartPolicy": "Never",
                    "containers": [{
                        "name": "create-buckets", "image": "public.ecr.aws/aws-cli/aws-cli:2.31.0",
                        "command": ["/bin/sh", "-c", script],
                        "env": [
                            {"name": "S3_ENDPOINT", "value": "http://" + self.endpoint},
                            {"name": "AWS_DEFAULT_REGION", "value": "us-east-1"},
                            {"name": "AWS_EC2_METADATA_DISABLED", "value": "true"},
                            {"name": "AWS_ACCESS_KEY_ID", "valueFrom": {"secretKeyRef": {
                                "name": "rustfs-credentials", "key": "RUSTFS_ACCESS_KEY",
                            }}},
                            {"name": "AWS_SECRET_ACCESS_KEY", "valueFrom": {"secretKeyRef": {
                                "name": "rustfs-credentials", "key": "RUSTFS_SECRET_KEY",
                            }}},
                        ],
                        "resources": {
                            "requests": {"cpu": "50m", "memory": "128Mi"},
                            "limits": {"cpu": "500m", "memory": "256Mi"},
                        },
                    }],
                }},
            },
            opts=pulumi.ResourceOptions(parent=self, depends_on=[self.release]),
        )
        pulumi.export("rustfs_endpoint", "http://192.168.1.37:9000")
        pulumi.export("rustfs_console", "http://192.168.1.38:9001")
