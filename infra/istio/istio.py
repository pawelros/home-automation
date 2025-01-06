import pulumi
import pulumi_kubernetes as kubernetes
from pulumi_kubernetes.helm.v3 import Release, ReleaseArgs, RepositoryOptsArgs


class Istio(pulumi.ComponentResource):
    def __init__(self, opts=None):
        super().__init__(
            "istio",
            "istio",
            None,
        )
        istio_base = Release(
            "istio-base",
            ReleaseArgs(
                chart="base",
                namespace="istio-system",
                create_namespace=True,
                atomic=True,
                timeout=120,
                version="1.24.2",
                repository_opts=RepositoryOptsArgs(
                    repo="https://istio-release.storage.googleapis.com/charts",
                ),
                values={"defaultRevision": "default"},
            ),
            opts=pulumi.ResourceOptions(parent=self),
        )

        istiod = Release(
            "istiod",
            ReleaseArgs(
                chart="istiod",
                namespace="istio-system",
                create_namespace=False,
                atomic=True,
                timeout=120,
                version="1.24.2",
                repository_opts=RepositoryOptsArgs(
                    repo="https://istio-release.storage.googleapis.com/charts",
                ),
                values={},
            ),
            opts=pulumi.ResourceOptions(parent=self, depends_on=[istio_base]),
        )

        gateway = Release(
            "gateway",
            ReleaseArgs(
                chart="gateway",
                namespace="istio-system",
                create_namespace=False,
                atomic=True,
                timeout=120,
                version="1.24.2",
                repository_opts=RepositoryOptsArgs(
                    repo="https://istio-release.storage.googleapis.com/charts",
                ),
                values={},
            ),
            opts=pulumi.ResourceOptions(parent=self, depends_on=[istio_base]),
        )

        # bookinfo_manifest = kubernetes.yaml.ConfigFile(
        #     "bookinfo-manifest",
        #     file="https://raw.githubusercontent.com/istio/istio/release-1.24/samples/bookinfo/platform/kube/bookinfo.yaml",
        # )

        # ingress_manifest = kubernetes.yaml.ConfigFile(
        #     "ingress-manifest",
        #     file="https://raw.githubusercontent.com/istio/istio/release-1.24/samples/bookinfo/networking/bookinfo-gateway.yaml",
        # )

        deployment = kubernetes.apps.v1.Deployment(
            "nginx",
            opts=pulumi.ResourceOptions(parent=self),
            metadata=kubernetes.meta.v1.ObjectMetaArgs(
                name="nginx",
                namespace="default",
                labels={
                    "app": "nginx",
                },
            ),
            spec=kubernetes.apps.v1.DeploymentSpecArgs(
                replicas=3,
                selector=kubernetes.meta.v1.LabelSelectorArgs(
                    match_labels={
                        "app": "nginx",
                    },
                ),
                template=kubernetes.core.v1.PodTemplateSpecArgs(
                    metadata=kubernetes.meta.v1.ObjectMetaArgs(
                        labels={
                            "app": "nginx",
                        },
                    ),
                    spec=kubernetes.core.v1.PodSpecArgs(
                        containers=[
                            kubernetes.core.v1.ContainerArgs(
                                image="nginx:latest",
                                name="nginx",
                                ports=[
                                    kubernetes.core.v1.ContainerPortArgs(
                                        container_port=80,
                                    )
                                ],
                            )
                        ],
                    ),
                ),
            ),
        )

        gateway = kubernetes.yaml.ConfigFile(
            "nginx-ingress-gateway",
            file="./istio/nginx-ingress-gateway.yaml"
        )

        virtual_service = kubernetes.yaml.ConfigFile(
            "nginx-virtual-service",
            file="./istio/nginx-virtual-service.yaml"
        )

        load_balancer_service = kubernetes.core.v1.Service(
            "nginx-lb",
            opts=pulumi.ResourceOptions(parent=self),
            metadata=kubernetes.meta.v1.ObjectMetaArgs(
                name="nginx-lb",
                namespace="default",
            ),
            spec=kubernetes.core.v1.ServiceSpecArgs(
                ports=[
                    kubernetes.core.v1.ServicePortArgs(
                        name="http",
                        port=80,
                        protocol="TCP",
                        target_port=80,
                    ),
                ],
                selector={
                    "app": "nginx-ingress-gateway",
                },
                type="LoadBalancer",
                external_traffic_policy="Local",
            ),
        )

        # Export the name of the release
        pulumi.export("istio_base_version", istio_base.version)
        pulumi.export("istiod_version", istiod.version)
