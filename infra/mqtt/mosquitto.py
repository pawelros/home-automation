import pulumi
import pulumi_kubernetes as kubernetes


class Mosquitto(pulumi.ComponentResource):
    def __init__(self, ns: kubernetes.core.v1.Namespace, opts=None):
        super().__init__(
            "mosquitto",
            "mosquitto",
            None,
            opts=pulumi.ResourceOptions(parent=ns),
        )

        deployment = kubernetes.apps.v1.Deployment(
            "mosquitto",
            opts=pulumi.ResourceOptions(parent=self),
            metadata=kubernetes.meta.v1.ObjectMetaArgs(
                name="mosquitto",
                namespace=ns,
                labels={
                    "app": "mosquitto",
                },
            ),
            spec=kubernetes.apps.v1.DeploymentSpecArgs(
                replicas=1,
                selector=kubernetes.meta.v1.LabelSelectorArgs(
                    match_labels={
                        "app": "mosquitto",
                    },
                ),
                template=kubernetes.core.v1.PodTemplateSpecArgs(
                    metadata=kubernetes.meta.v1.ObjectMetaArgs(
                        labels={
                            "app": "mosquitto",
                        },
                    ),
                    spec=kubernetes.core.v1.PodSpecArgs(
                        containers=[
                            kubernetes.core.v1.ContainerArgs(
                                image="eclipse-mosquitto:2.0.19",
                                name="mosquitto",
                                command=["mosquitto"],
                                args=[
                                    "-c",
                                    "/mosquitto-no-auth.conf",
                                ],
                                ports=[
                                    kubernetes.core.v1.ContainerPortArgs(
                                        container_port=1883,
                                    ),
                                    kubernetes.core.v1.ContainerPortArgs(
                                        container_port=9001,
                                    ),
                                ],
                            )
                        ],
                        security_context=kubernetes.core.v1.PodSecurityContextArgs(
                            run_as_user=1883,
                            run_as_group=1883,
                        ),
                        affinity=kubernetes.core.v1.AffinityArgs(
                            pod_anti_affinity=kubernetes.core.v1.PodAntiAffinityArgs(
                                required_during_scheduling_ignored_during_execution=[
                                    kubernetes.core.v1.PodAffinityTermArgs(
                                        label_selector=kubernetes.meta.v1.LabelSelectorArgs(
                                            match_expressions=[
                                                kubernetes.meta.v1.LabelSelectorRequirementArgs(
                                                    key="app",
                                                    operator="In",
                                                    values=["mosquitto"],
                                                ),
                                            ],
                                        ),
                                        topology_key="kubernetes.io/hostname",
                                    ),
                                ],
                            ),
                        ),
                    ),
                ),
            ),
        )

        service = kubernetes.core.v1.Service(
            "mosquitto",
            opts=pulumi.ResourceOptions(parent=self),
            metadata=kubernetes.meta.v1.ObjectMetaArgs(
                name="mosquitto",
                namespace=ns,
            ),
            spec=kubernetes.core.v1.ServiceSpecArgs(
                ports=[
                    kubernetes.core.v1.ServicePortArgs(
                        name="mqtt",
                        port=1883,
                        protocol="TCP",
                        target_port=1883,
                    ),
                    kubernetes.core.v1.ServicePortArgs(
                        name="wss",
                        port=9001,
                        protocol="TCP",
                        target_port=9001,
                    ),
                ],
                selector={
                    "app": "mosquitto",
                },
                type="LoadBalancer",
                external_traffic_policy="Local",
            ),
        )
