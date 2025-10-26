import pulumi
import pulumi_kubernetes as kubernetes


class MetalLb(pulumi.ComponentResource):
    def __init__(self, opts=None):
        ns = kubernetes.core.v1.Namespace(
            "metal-lb",
            metadata=kubernetes.meta.v1.ObjectMetaArgs(
                name="metal-lb",
                labels={
                    "pod-security.kubernetes.io/enforce": "privileged",
                    "pod-security.kubernetes.io/audit": "privileged",
                    "pod-security.kubernetes.io/warn": "privileged",
                },
            ),
        )
        super().__init__(
            "metal-lb",
            "metal-lb",
            None,
            opts=pulumi.ResourceOptions(parent=ns),
        )

        metallb = kubernetes.helm.v3.Release(
            "metallb",
            name="metallb",
            chart="metallb",
            version="0.14.8",  # Pin to specific version to prevent auto-upgrades
            namespace=ns.metadata.name,
            repository_opts={
                "repo": "https://metallb.github.io/metallb",
            },
            values={
                "speaker": {
                    "frr": {
                        "enabled": False,
                    }
                }
            },
            opts=pulumi.ResourceOptions(parent=self, depends_on=[ns]),
        )
        ip_address_pool = kubernetes.apiextensions.CustomResource(
            "ip-address-pool",
            api_version="metallb.io/v1beta1",
            kind="IPAddressPool",
            metadata=kubernetes.meta.v1.ObjectMetaArgs(
                name="ip-address-pool",
                namespace=ns.metadata.name,
            ),
            spec={
                "addresses": ["192.168.1.30-192.168.1.255"],
            },
            opts=pulumi.ResourceOptions(parent=metallb),
        )
        l2_advertisement = kubernetes.apiextensions.CustomResource(
            "l2-advertisement",
            api_version="metallb.io/v1beta1",
            kind="L2Advertisement",
            metadata=kubernetes.meta.v1.ObjectMetaArgs(
                name="l2-advertisement",
                namespace=ns.metadata.name,
            ),
            spec={},
            opts=pulumi.ResourceOptions(parent=ip_address_pool),
        )
