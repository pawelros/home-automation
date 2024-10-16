import pulumi
import pulumi_kubernetes as kubernetes


class Ubuntu(pulumi.ComponentResource):
    def __init__(self, ns: kubernetes.core.v1.Namespace, opts=None):
        super().__init__("ubuntu", "ubuntu", None, opts=pulumi.ResourceOptions(parent=ns))

        deployment = kubernetes.apps.v1.Deployment(
            "ubuntu_deployment",
            opts=pulumi.ResourceOptions(parent=self),
            metadata=kubernetes.meta.v1.ObjectMetaArgs(
                name="ubuntu",
                namespace=ns.metadata["name"],
                labels={
                    "app": "ubuntu",
                },
            ),
            spec=kubernetes.apps.v1.DeploymentSpecArgs(
                replicas=1,
                selector=kubernetes.meta.v1.LabelSelectorArgs(
                    match_labels={
                        "app": "ubuntu",
                    },
                ),
                template=kubernetes.core.v1.PodTemplateSpecArgs(
                    metadata=kubernetes.meta.v1.ObjectMetaArgs(
                        labels={
                            "app": "ubuntu",
                        },
                    ),
                    spec=kubernetes.core.v1.PodSpecArgs(
                        containers=[
                            kubernetes.core.v1.ContainerArgs(
                                image="ubuntu:latest",
                                name="ubuntu",
                                command=["sleep", "604800"],
                                ports=[
                                    kubernetes.core.v1.ContainerPortArgs(
                                        container_port=22,
                                    )
                                ],
                            )
                        ],
                    ),
                ),
            ),
        )