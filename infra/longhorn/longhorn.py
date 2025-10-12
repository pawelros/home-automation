import pulumi
import pulumi_kubernetes as kubernetes


class Longhorn(pulumi.ComponentResource):
    def __init__(self, opts=None):
        ns = kubernetes.core.v1.Namespace(
            "longhorn",
            metadata=kubernetes.meta.v1.ObjectMetaArgs(
                name="longhorn",
                labels={
                    "pod-security.kubernetes.io/enforce": "privileged",
                    "pod-security.kubernetes.io/audit": "privileged",
                    "pod-security.kubernetes.io/warn": "privileged",
                },
            ),
        )
        super().__init__(
            "longhorn",
            "longhorn",
            None,
            opts=pulumi.ResourceOptions(parent=ns),
        )

        longhorn = kubernetes.helm.v3.Release(
            "longhorn",
            name="longhorn",
            chart="longhorn",
            version="1.10.0",
            namespace=ns.metadata.name,
            repository_opts={
                "repo": "https://charts.longhorn.io",
            },
            values={
                "defaultSettings": {
                    "defaultDataPath": "/var/lib/longhorn",
                },
                "persistence": {
                    "defaultClassReplicaCount": 1,
                },
            },
            opts=pulumi.ResourceOptions(parent=self, depends_on=[ns]),
        )

        _ = kubernetes.core.v1.Service(
            "longhorn-ui",
            opts=pulumi.ResourceOptions(parent=self),
            metadata=kubernetes.meta.v1.ObjectMetaArgs(
                name="longhorn-ui",
                namespace="longhorn",
            ),
            spec=kubernetes.core.v1.ServiceSpecArgs(
                ports=[
                    kubernetes.core.v1.ServicePortArgs(
                        name="http",
                        port=80,
                        protocol="TCP",
                        target_port=8000,
                    ),
                ],
                selector={
                    "app": "longhorn-ui",
                },
                type="LoadBalancer",
                external_traffic_policy="Local",
            ),
        )
