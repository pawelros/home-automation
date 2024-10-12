import pulumi
import pulumi_kubernetes as kubernetes
from cert_manager.cert_manager import CertManager


class EmqxOperator(pulumi.ComponentResource):
    def __init__(self, certManager: CertManager, opts=None):
        ns = kubernetes.core.v1.Namespace(
            "emqx-operator-system",
            metadata=kubernetes.meta.v1.ObjectMetaArgs(
                name="emqx-operator-system",
            ),
        )
        super().__init__(
            "emqxOperator", "emqxOperator", None, opts=pulumi.ResourceOptions(parent=ns)
        )

        emqx = kubernetes.helm.v3.Release(
            "emqx-operator",
            name="emqx-operator",
            chart="emqx-operator",
            namespace=ns.metadata.name,
            repository_opts={
                "repo": "https://repos.emqx.io/charts",
            },
            # values={
            #     "controller": {
            #         "enableCustomResources": False,
            #         "appprotect": {
            #             "enable": False,
            #         },
            #         "appprotectdos": {
            #             "enable": False,
            #         },
            #         "service": {
            #             "extraLabels": app_labels,
            #         },
            #     },
            # },
            # version="5.8.0",
            opts=pulumi.ResourceOptions(parent=self, depends_on=[certManager]),
        )
