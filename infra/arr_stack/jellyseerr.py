import pulumi
import pulumi_kubernetes as kubernetes
from pulumi_kubernetes.apps.v1 import Deployment, DeploymentSpecArgs
from pulumi_kubernetes.core.v1 import (
    Service, ServiceSpecArgs, ServicePortArgs,
    PersistentVolumeClaim, PersistentVolumeClaimSpecArgs,
    ContainerArgs, PodSpecArgs, PodTemplateSpecArgs,
    VolumeArgs, VolumeMountArgs, EnvVarArgs,
    ResourceRequirementsArgs,
    HTTPGetActionArgs, ProbeArgs
)
from pulumi_kubernetes.meta.v1 import LabelSelectorArgs, ObjectMetaArgs


class Jellyseerr(pulumi.ComponentResource):
    def __init__(self, namespace: kubernetes.core.v1.Namespace, opts=None):
        super().__init__(
            "jellyseerr",
            "jellyseerr",
            None,
            opts=opts,
        )

        # Create PVC for Jellyseerr config
        self.pvc = PersistentVolumeClaim(
            "jellyseerr-config",
            metadata=ObjectMetaArgs(
                name="jellyseerr-config",
                namespace=namespace.metadata.name
            ),
            spec=PersistentVolumeClaimSpecArgs(
                access_modes=["ReadWriteOnce"],
                storage_class_name="longhorn",
                resources=kubernetes.core.v1.ResourceRequirementsArgs(
                    requests={"storage": "5Gi"}
                )
            ),
            opts=pulumi.ResourceOptions(parent=self)
        )

        # Create Jellyseerr Deployment
        self.deployment = Deployment(
            "jellyseerr",
            metadata=ObjectMetaArgs(
                name="jellyseerr",
                namespace=namespace.metadata.name,
                labels={"app": "jellyseerr"}
            ),
            spec=DeploymentSpecArgs(
                replicas=1,
                selector=LabelSelectorArgs(
                    match_labels={"app": "jellyseerr"}
                ),
                template=PodTemplateSpecArgs(
                    metadata=ObjectMetaArgs(
                        labels={"app": "jellyseerr"}
                    ),
                    spec=PodSpecArgs(
                        security_context=kubernetes.core.v1.PodSecurityContextArgs(
                            fs_group=1000
                        ),
                        containers=[
                            ContainerArgs(
                                name="jellyseerr",
                                image="fallenbagel/jellyseerr:1.9.2",
                                ports=[kubernetes.core.v1.ContainerPortArgs(
                                    container_port=5055,
                                    name="http"
                                )],
                                env=[
                                    EnvVarArgs(name="TZ", value="UTC"),
                                    EnvVarArgs(name="LOG_LEVEL", value="info")
                                ],
                                volume_mounts=[
                                    VolumeMountArgs(
                                        name="config",
                                        mount_path="/app/config"
                                    )
                                ],
                                resources=ResourceRequirementsArgs(
                                    limits={
                                        "cpu": "1000m",
                                        "memory": "1Gi"
                                    },
                                    requests={
                                        "cpu": "100m",
                                        "memory": "256Mi"
                                    }
                                ),
                                security_context=kubernetes.core.v1.SecurityContextArgs(
                                    run_as_user=1000,
                                    run_as_group=1000,
                                    run_as_non_root=True,
                                    allow_privilege_escalation=False,
                                    read_only_root_filesystem=False
                                ),
                                liveness_probe=ProbeArgs(
                                    http_get=HTTPGetActionArgs(
                                        path="/api/v1/status",
                                        port=5055
                                    ),
                                    initial_delay_seconds=30,
                                    period_seconds=30,
                                    timeout_seconds=10,
                                    failure_threshold=5
                                ),
                                readiness_probe=ProbeArgs(
                                    http_get=HTTPGetActionArgs(
                                        path="/api/v1/status",
                                        port=5055
                                    ),
                                    initial_delay_seconds=30,
                                    period_seconds=30,
                                    timeout_seconds=10,
                                    failure_threshold=5
                                )
                            )
                        ],
                        volumes=[
                            VolumeArgs(
                                name="config",
                                persistent_volume_claim=kubernetes.core.v1.PersistentVolumeClaimVolumeSourceArgs(
                                    claim_name=self.pvc.metadata.name
                                )
                            )
                        ]
                    )
                )
            ),
            opts=pulumi.ResourceOptions(parent=self, depends_on=[self.pvc])
        )

        # Create LoadBalancer Service
        self.service = Service(
            "jellyseerr",
            metadata=ObjectMetaArgs(
                name="jellyseerr",
                namespace=namespace.metadata.name,
                annotations={
                    "metallb.universe.tf/allow-shared-ip": "jellyseerr"
                }
            ),
            spec=ServiceSpecArgs(
                type="LoadBalancer",
                load_balancer_ip="192.168.1.42",
                selector={"app": "jellyseerr"},
                ports=[
                    ServicePortArgs(
                        name="http",
                        port=80,
                        target_port=5055,
                        protocol="TCP"
                    )
                ]
            ),
            opts=pulumi.ResourceOptions(parent=self, depends_on=[self.deployment])
        )

        # Store references
        self.namespace = namespace
        
        # Export useful information
        self.service_ip = pulumi.Output.concat("192.168.1.42")
        self.web_url = pulumi.Output.concat("http://192.168.1.42")
        self.api_url = pulumi.Output.concat("http://192.168.1.42/api")
