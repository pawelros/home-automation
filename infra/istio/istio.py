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

        kiali_operator = Release(
            "kiali-operator",
            ReleaseArgs(
                chart="kiali-operator",
                namespace="istio-system",
                atomic=True,
                timeout=120,
                repository_opts=RepositoryOptsArgs(
                    repo="https://kiali.org/helm-charts",
                ),
                values={
                    "cr": {
                        "create": True,
                        "namespace": "istio-system",
                        "spec": {
                            "auth": {
                                "strategy": "anonymous",
                            },
                            "deployment": {
                                "cluster_wide_access": True,
                            },
                        },
                    }
                },
            ),
            opts=pulumi.ResourceOptions(parent=self),
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

        nginx_service = kubernetes.core.v1.Service(
            "nginx-service",
            opts=pulumi.ResourceOptions(parent=self),
            metadata=kubernetes.meta.v1.ObjectMetaArgs(
                name="nginx-service",
                namespace="default",
                labels={
                    "app": "nginx",
                },
            ),
            spec=kubernetes.core.v1.ServiceSpecArgs(
                ports=[
                    kubernetes.core.v1.ServicePortArgs(
                        name="http",
                        port=80,
                        target_port=80,
                        protocol="TCP",
                    ),
                ],
                selector={
                    "app": "nginx",
                },
                type="ClusterIP",
            ),
        )

        gateway = kubernetes.yaml.ConfigFile(
            "zigbee2mqtt-ingress-gateway",
            file="./istio/zigbee2mqtt-ingress-gateway.yaml",
        )

        virtual_service = kubernetes.yaml.ConfigFile(
            "zigbee2mqtt-virtual-service",
            file="./istio/zigbee2mqtt-virtual-service.yaml",
        )

        load_balancer_service = kubernetes.core.v1.Service(
            "zigbee2mqtt-lb",
            opts=pulumi.ResourceOptions(parent=self),
            metadata=kubernetes.meta.v1.ObjectMetaArgs(
                name="zigbee2mqtt-lb",
                namespace="home-automation",
            ),
            spec=kubernetes.core.v1.ServiceSpecArgs(
                ports=[
                    kubernetes.core.v1.ServicePortArgs(
                        name="http",
                        port=8080,
                        protocol="TCP",
                        target_port=8080,
                    ),
                ],
                selector={
                    "app": "zigbee2mqtt",
                },
                type="LoadBalancer",
                external_traffic_policy="Local",
            ),
        )

        # Export the name of the release
        pulumi.export("istio_base_version", istio_base.version)
        pulumi.export("istiod_version", istiod.version)
