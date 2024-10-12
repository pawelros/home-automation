import pulumi
import pulumi_kubernetes as kubernetes


class Ebusd(pulumi.ComponentResource):
    def __init__(self, ns: kubernetes.core.v1.Namespace, opts=None):
        super().__init__("ebusd", "ebusd", None, opts=pulumi.ResourceOptions(parent=ns))

        deployment = kubernetes.apps.v1.Deployment(
            "ebusd",
            opts=pulumi.ResourceOptions(parent=self),
            metadata=kubernetes.meta.v1.ObjectMetaArgs(
                name="ebusd",
                namespace=ns,
                labels={
                    "app": "ebusd",
                },
            ),
            spec=kubernetes.apps.v1.DeploymentSpecArgs(
                replicas=1,
                selector=kubernetes.meta.v1.LabelSelectorArgs(
                    match_labels={
                        "app": "ebusd",
                    },
                ),
                template=kubernetes.core.v1.PodTemplateSpecArgs(
                    metadata=kubernetes.meta.v1.ObjectMetaArgs(
                        labels={
                            "app": "ebusd",
                        },
                    ),
                    spec=kubernetes.core.v1.PodSpecArgs(
                        containers=[
                            kubernetes.core.v1.ContainerArgs(
                                image="john30/ebusd:v23.3",
                                name="ebusd",
                                args=[
                                    "--scanconfig",
                                    "-d",
                                    "192.168.1.185:9999",
                                    "--latency=20",
                                ],
                                ports=[
                                    kubernetes.core.v1.ContainerPortArgs(
                                        container_port=8888,
                                    )
                                ],
                            )
                        ],
                    ),
                ),
            ),
        )
