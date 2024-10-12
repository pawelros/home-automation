import pulumi
import pulumi_kubernetes as kubernetes
from pulumi_kubernetes_cert_manager import CertManager as CM, ReleaseArgs

class CertManager(pulumi.ComponentResource):
    def __init__(self, opts=None):
        ns = kubernetes.core.v1.Namespace(
            "cert-manager",
            metadata=kubernetes.meta.v1.ObjectMetaArgs(
                name="cert-manager",
            ),
        )
        super().__init__(
            "certManager", "certManager", None, opts=pulumi.ResourceOptions(parent=ns)
        )

        # Install cert-manager into our cluster.
        manager = CM('cert-manager',
                            install_crds=True,
                            helm_options=ReleaseArgs(
                                namespace=ns.metadata.name,
                            ))
