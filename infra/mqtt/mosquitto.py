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

        primary_deployment = kubernetes.apps.v1.Deployment(
            "mosquitto-primary",
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
                            "type": "primary",
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
                                    "/mosquitto/config/mosquitto.conf",
                                ],
                                volume_mounts=[kubernetes.core.v1.VolumeMountArgs(
                                    name="config",
                                    mount_path="/mosquitto/config",
                                )],
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
                        volumes=[kubernetes.core.v1.VolumeArgs(
                            name="config",
                            config_map=kubernetes.core.v1.ConfigMapVolumeSourceArgs(
                                name="primary-config",
                            ),
                        )]
                    ),
                ),
            ),
        )

        primary_config_map = kubernetes.core.v1.ConfigMap(
            "mosquitto-primary-config",
            opts=pulumi.ResourceOptions(parent=self),
            metadata=kubernetes.meta.v1.ObjectMetaArgs(
                name="primary-config",
                namespace=ns,
            ),
            data={
                "mosquitto.conf": """
listener 1883
allow_anonymous true
persistence false
log_dest stdout
log_type all
""",
            },
        )

        load_balancer_service = kubernetes.core.v1.Service(
            "mosquitto-lb",
            opts=pulumi.ResourceOptions(parent=self),
            metadata=kubernetes.meta.v1.ObjectMetaArgs(
                name="mosquitto-lb",
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

        failover_config_map = kubernetes.core.v1.ConfigMap(
            "mosquitto-bridge-config",
            opts=pulumi.ResourceOptions(parent=self),
            metadata=kubernetes.meta.v1.ObjectMetaArgs(
            name="bridge-config",
            namespace=ns,
            ),
            data={
                "mosquitto.conf": """
listener 1883
allow_anonymous true
persistence false
log_dest stdout
log_type all

connection broker0
address mosquitto-primary.home-automation.svc.cluster.local:1883
topic # both 0
""",
            },
        )

        primary_selector_service = kubernetes.core.v1.Service(
            "mosquitto-primary",
            opts=pulumi.ResourceOptions(parent=self),
            metadata=kubernetes.meta.v1.ObjectMetaArgs(
                name="mosquitto-primary",
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
                    "type": "primary",
                },
                type="LoadBalancer",
                external_traffic_policy="Local",
            ),
        )

        failover_deployment = kubernetes.apps.v1.Deployment(
            "mosquitto-failover",
            opts=pulumi.ResourceOptions(parent=self),
            metadata=kubernetes.meta.v1.ObjectMetaArgs(
                name="mosquitto-failover",
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
                            "type": "bridge",
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
                                    "/mosquitto/config/mosquitto.conf",
                                ],
                                ports=[
                                    kubernetes.core.v1.ContainerPortArgs(
                                        container_port=1883,
                                    ),
                                    kubernetes.core.v1.ContainerPortArgs(
                                        container_port=9001,
                                    ),
                                ],
                                volume_mounts=[kubernetes.core.v1.VolumeMountArgs(
                                    name="config",
                                    mount_path="/mosquitto/config",
                                )]
                            )
                        ],
                        security_context=kubernetes.core.v1.PodSecurityContextArgs(
                            run_as_user=1883,
                            run_as_group=1883,
                        ),
                        volumes=[kubernetes.core.v1.VolumeArgs(
                            name="config",
                            config_map=kubernetes.core.v1.ConfigMapVolumeSourceArgs(
                                name=failover_config_map.metadata["name"],
                            ),
                        )]
                    ),
                ),
            ),
        )
