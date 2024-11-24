import pulumi
from pulumi_kubernetes.helm.v3 import Release, ReleaseArgs, RepositoryOptsArgs


class MetricsServer(pulumi.ComponentResource):
    def __init__(self, opts=None):
        super().__init__(
            "metrics-server",
            "metrics-server",
            None,
        )
        metrics_server = Release(
            "metrics-server",
            ReleaseArgs(
                chart="metrics-server",
                namespace="kube-system",
                atomic=True,
                timeout=120,
                version="3.12.2",
                repository_opts=RepositoryOptsArgs(
                    repo="https://kubernetes-sigs.github.io/metrics-server/",
                ),
                values={
                    "defaultArgs": [
                        "--cert-dir=/tmp",
                        "--kubelet-preferred-address-types=InternalIP,ExternalIP,Hostname",
                        "--kubelet-use-node-status-port",
                        "--metric-resolution=15s",
                        "--kubelet-insecure-tls",
                    ]
                },
            ),
            opts=pulumi.ResourceOptions(parent=self),
        )
