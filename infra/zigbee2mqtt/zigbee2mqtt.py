import pulumi
import pulumi_kubernetes as k8s
from pv.pv import Pv


class Zigbee2Mqtt(pulumi.ComponentResource):
    def __init__(self, ns: k8s.core.v1.Namespace, pv: Pv, opts=None):
        super().__init__(
            "zigbee2mqtt",
            "zigbee2mqtt",
            None,
        )

        pvc = k8s.core.v1.PersistentVolumeClaim(
            "zigbee2mqtt-pvc",
            metadata=k8s.meta.v1.ObjectMetaArgs(
                name="zigbee2mqtt-pvc",
                namespace=ns,
            ),
            spec=k8s.core.v1.PersistentVolumeClaimSpecArgs(
                storage_class_name="local-storage",
                volume_name=pv.pv_node_1.metadata["name"],
                access_modes=["ReadWriteOnce"],
                resources=k8s.core.v1.ResourceRequirementsArgs(
                    requests={"storage": "0.5Gi"}
                ),
            ),
            opts=pulumi.ResourceOptions(parent=self),
        )

        service = k8s.core.v1.Service(
            "zigbee2mqtt-service",
            metadata=k8s.meta.v1.ObjectMetaArgs(
                name="zigbee2mqtt-service",
                namespace=ns,
                labels={
                    "app": "zigbee2mqtt",
                },
            ),
            spec=k8s.core.v1.ServiceSpecArgs(
                ports=[
                    k8s.core.v1.ServicePortArgs(
                        port=8099,
                        target_port="http",
                    )
                ],
                selector={
                    "app": "zigbee2mqtt",
                },
            ),
        )

        deployment = k8s.apps.v1.Deployment(
            "zigbee2mqtt-deployment",
            opts=pulumi.ResourceOptions(parent=self),
            metadata=k8s.meta.v1.ObjectMetaArgs(
                name="zigbee2mqtt",
                namespace=ns,
                labels={
                    "app": "zigbee2mqtt",
                },
            ),
            spec=k8s.apps.v1.DeploymentSpecArgs(
                replicas=1,
                selector=k8s.meta.v1.LabelSelectorArgs(
                    match_labels={
                        "app": "zigbee2mqtt",
                    },
                ),
                template=k8s.core.v1.PodTemplateSpecArgs(
                    metadata=k8s.meta.v1.ObjectMetaArgs(
                        labels={
                            "app": "zigbee2mqtt",
                        },
                    ),
                    spec=k8s.core.v1.PodSpecArgs(
                        node_selector={"kubernetes.io/hostname": "k8s-node-1"},
                        containers=[
                            k8s.core.v1.ContainerArgs(
                                resources=k8s.core.v1.ResourceRequirementsArgs(
                                    requests={"cpu": "200m", "memory": "128Mi"},
                                    limits={"memory": "256Mi"},
                                ),
                                image="koenkk/zigbee2mqtt:2.0.0",
                                name="zigbee2mqtt",
                                ports=[
                                    k8s.core.v1.ContainerPortArgs(
                                        container_port=8080,
                                        name="http",
                                    ),
                                ],
                                env=[
                                    k8s.core.v1.EnvVarArgs(
                                        name="ZIGBEE2MQTT_DATA", value="/data"
                                    ),
                                    k8s.core.v1.EnvVarArgs(
                                        name="TZ", value="Europe/Warsaw"
                                    ),
                                ],
                                volume_mounts=[
                                    k8s.core.v1.VolumeMountArgs(
                                        name="data",
                                        mount_path="/data",
                                    ),
                                    k8s.core.v1.VolumeMountArgs(
                                        name="usb",
                                        mount_path="/dev/ttyUSB0",
                                    ),
                                    k8s.core.v1.VolumeMountArgs(
                                        name="udev",
                                        mount_path="/run/udev",
                                    ),
                                ],
                                security_context=k8s.core.v1.SecurityContextArgs(
                                    privileged=True
                                ),
                            )
                        ],
                        volumes=[
                            k8s.core.v1.VolumeArgs(
                                name="data",
                                persistent_volume_claim=k8s.core.v1.PersistentVolumeClaimVolumeSourceArgs(
                                    claim_name=pvc.metadata["name"],
                                ),
                            ),
                            k8s.core.v1.VolumeArgs(
                                name="usb",
                                host_path=k8s.core.v1.HostPathVolumeSourceArgs(
                                    path="/dev/ttyUSB0",
                                ),
                            ),
                            k8s.core.v1.VolumeArgs(
                                name="udev",
                                host_path=k8s.core.v1.HostPathVolumeSourceArgs(
                                    path="/run/udev",
                                ),
                            ),
                        ],
                    ),
                ),
            ),
        )


#         volumeMounts:
#         - name: data
#           mountPath: /data
#         - name: usb
#           mountPath: /dev/ttyUSB0
#         - name: udev
#           mountPath: /run/udev
#         securityContext:
#           privileged: true
#       volumes:
#       - name: data
#         persistentVolumeClaim:
#           claimName: zigbee2mqtt-data
#       - name: usb
#         hostPath:
#           path: /dev/ttyUSB0
#       - name: udev
#         hostPath:
#           path: /run/udev
