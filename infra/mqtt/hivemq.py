import pulumi
import pulumi_kubernetes as kubernetes
from cert_manager.cert_manager import CertManager


class HiveMqOperator(pulumi.ComponentResource):
    def __init__(self, opts=None):
        ns = kubernetes.core.v1.Namespace(
            "hivemq",
            metadata=kubernetes.meta.v1.ObjectMetaArgs(
                name="hivemq",
            ),
        )
        super().__init__(
            "hivemqOperator",
            "hivemqOperator",
            None,
            opts=pulumi.ResourceOptions(parent=ns),
        )

        hivemq_operator = kubernetes.helm.v3.Release(
            "hivemq-platform-operator",
            name="hivemq-platform-operator",
            chart="hivemq-platform-operator",
            namespace=ns.metadata.name,
            repository_opts={
                "repo": "https://hivemq.github.io/helm-charts",
            },
            values={"resources": {"cpu": "4096m", "memory": "8Gi"}},
            # version="5.8.0",
            opts=pulumi.ResourceOptions(parent=self, depends_on=[]),
        )

        hivemq_platform = kubernetes.helm.v3.Release(
            "hivemq-platform",
            name="hivemq-platform",
            chart="hivemq-platform",
            namespace=ns.metadata.name,
            repository_opts={
                "repo": "https://hivemq.github.io/helm-charts",
            },
            values={"nodeCount": "4"},
            # version="5.8.0",
            opts=pulumi.ResourceOptions(parent=self, depends_on=[]),
        )

        # service = kubernetes.core.v1.Service(
        #     "service",
        #     spec=kubernetes.core.v1.ServiceSpecArgs(
        #         ports=[
        #             kubernetes.core.v1.ServicePortArgs(
        #                 port=1883,
        #                 protocol="TCP",
        #                 target_port=1883,
        #             )
        #         ],
        #         selector={
        #             "app": "hivemq-platform",
        #         },
        #     ),
        # )

    # hivemq = kubernetes.yaml.ConfigFile("hivemq", "mqtt/hivemq_open_source.yaml", opts=pulumi.ResourceOptions(parent=self, depends_on=[hivemq_operator]))
