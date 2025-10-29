import pulumi
import pulumi_kubernetes as kubernetes


class UnifiController(pulumi.ComponentResource):
    def __init__(self, opts=None):
        super().__init__(
            "unifi-controller",
            "unifi-controller",
            None,
        )

        # Create dedicated namespace for UniFi Controller
        ns = kubernetes.core.v1.Namespace(
            "unify",
            metadata=kubernetes.meta.v1.ObjectMetaArgs(
                name="unify",
            ),
            opts=pulumi.ResourceOptions(parent=self),
        )

        # Create PersistentVolumeClaim for MongoDB
        mongodb_pvc = kubernetes.core.v1.PersistentVolumeClaim(
            "unifi-mongodb-data",
            metadata=kubernetes.meta.v1.ObjectMetaArgs(
                name="unifi-mongodb-data",
                namespace=ns.metadata.name,
            ),
            spec=kubernetes.core.v1.PersistentVolumeClaimSpecArgs(
                access_modes=["ReadWriteOnce"],
                storage_class_name="longhorn",
                resources=kubernetes.core.v1.VolumeResourceRequirementsArgs(
                    requests={
                        "storage": "2Gi",
                    },
                ),
            ),
            opts=pulumi.ResourceOptions(parent=self, depends_on=[ns]),
        )

        # Create MongoDB initialization ConfigMap
        mongodb_init_configmap = kubernetes.core.v1.ConfigMap(
            "unifi-mongodb-init",
            metadata=kubernetes.meta.v1.ObjectMetaArgs(
                name="unifi-mongodb-init",
                namespace=ns.metadata.name,
            ),
            data={
                "init-mongo.js": """
db = db.getSiblingDB('unifi');
db.createUser({
  user: 'unifi',
  pwd: 'unifi',
  roles: [
    { role: 'dbOwner', db: 'unifi' },
    { role: 'dbOwner', db: 'unifi_stat' },
    { role: 'dbOwner', db: 'unifi_audit' }
  ]
});
"""
            },
            opts=pulumi.ResourceOptions(parent=self, depends_on=[ns]),
        )

        # Create MongoDB Deployment
        mongodb_deployment = kubernetes.apps.v1.Deployment(
            "unifi-db",
            metadata=kubernetes.meta.v1.ObjectMetaArgs(
                name="unifi-db",
                namespace=ns.metadata.name,
                labels={
                    "app": "unifi-db",
                },
            ),
            spec=kubernetes.apps.v1.DeploymentSpecArgs(
                replicas=1,
                selector=kubernetes.meta.v1.LabelSelectorArgs(
                    match_labels={
                        "app": "unifi-db",
                    },
                ),
                template=kubernetes.core.v1.PodTemplateSpecArgs(
                    metadata=kubernetes.meta.v1.ObjectMetaArgs(
                        labels={
                            "app": "unifi-db",
                        },
                    ),
                    spec=kubernetes.core.v1.PodSpecArgs(
                        containers=[
                            kubernetes.core.v1.ContainerArgs(
                                name="mongodb",
                                image="mongo:4.4",
                                env=[
                                    kubernetes.core.v1.EnvVarArgs(
                                        name="MONGO_INITDB_ROOT_USERNAME",
                                        value="root",
                                    ),
                                    kubernetes.core.v1.EnvVarArgs(
                                        name="MONGO_INITDB_ROOT_PASSWORD",
                                        value="rootpassword",
                                    ),
                                ],
                                ports=[
                                    kubernetes.core.v1.ContainerPortArgs(
                                        name="mongodb",
                                        container_port=27017,
                                        protocol="TCP",
                                    ),
                                ],
                                volume_mounts=[
                                    kubernetes.core.v1.VolumeMountArgs(
                                        name="mongodb-data",
                                        mount_path="/data/db",
                                    ),
                                    kubernetes.core.v1.VolumeMountArgs(
                                        name="mongodb-init",
                                        mount_path="/docker-entrypoint-initdb.d",
                                    ),
                                ],
                                resources=kubernetes.core.v1.ResourceRequirementsArgs(
                                    requests={
                                        "cpu": "250m",
                                        "memory": "512Mi",
                                    },
                                    limits={
                                        "cpu": "1000m",
                                        "memory": "1Gi",
                                    },
                                ),
                            ),
                        ],
                        volumes=[
                            kubernetes.core.v1.VolumeArgs(
                                name="mongodb-data",
                                persistent_volume_claim=kubernetes.core.v1.PersistentVolumeClaimVolumeSourceArgs(
                                    claim_name=mongodb_pvc.metadata.name,
                                ),
                            ),
                            kubernetes.core.v1.VolumeArgs(
                                name="mongodb-init",
                                config_map=kubernetes.core.v1.ConfigMapVolumeSourceArgs(
                                    name=mongodb_init_configmap.metadata.name,
                                ),
                            ),
                        ],
                    ),
                ),
            ),
            opts=pulumi.ResourceOptions(parent=self, depends_on=[mongodb_pvc, mongodb_init_configmap]),
        )

        # Create MongoDB Service
        mongodb_service = kubernetes.core.v1.Service(
            "unifi-db",
            metadata=kubernetes.meta.v1.ObjectMetaArgs(
                name="unifi-db",
                namespace=ns.metadata.name,
            ),
            spec=kubernetes.core.v1.ServiceSpecArgs(
                type="ClusterIP",
                selector={
                    "app": "unifi-db",
                },
                ports=[
                    kubernetes.core.v1.ServicePortArgs(
                        name="mongodb",
                        port=27017,
                        target_port=27017,
                        protocol="TCP",
                    ),
                ],
            ),
            opts=pulumi.ResourceOptions(parent=self, depends_on=[mongodb_deployment]),
        )

        # Create PersistentVolumeClaim for UniFi data
        unifi_pvc = kubernetes.core.v1.PersistentVolumeClaim(
            "unifi-data",
            metadata=kubernetes.meta.v1.ObjectMetaArgs(
                name="unifi-data",
                namespace=ns.metadata.name,
            ),
            spec=kubernetes.core.v1.PersistentVolumeClaimSpecArgs(
                access_modes=["ReadWriteOnce"],
                storage_class_name="longhorn",
                resources=kubernetes.core.v1.VolumeResourceRequirementsArgs(
                    requests={
                        "storage": "5Gi",
                    },
                ),
            ),
            opts=pulumi.ResourceOptions(parent=self, depends_on=[ns]),
        )

        # Create Deployment for UniFi Controller
        unifi_deployment = kubernetes.apps.v1.Deployment(
            "unifi-controller",
            metadata=kubernetes.meta.v1.ObjectMetaArgs(
                name="unifi-controller",
                namespace=ns.metadata.name,
                labels={
                    "app": "unifi-controller",
                },
            ),
            spec=kubernetes.apps.v1.DeploymentSpecArgs(
                replicas=1,
                selector=kubernetes.meta.v1.LabelSelectorArgs(
                    match_labels={
                        "app": "unifi-controller",
                    },
                ),
                template=kubernetes.core.v1.PodTemplateSpecArgs(
                    metadata=kubernetes.meta.v1.ObjectMetaArgs(
                        labels={
                            "app": "unifi-controller",
                        },
                    ),
                    spec=kubernetes.core.v1.PodSpecArgs(
                        containers=[
                            kubernetes.core.v1.ContainerArgs(
                                name="unifi",
                                image="lscr.io/linuxserver/unifi-network-application:latest",
                                env=[
                                    kubernetes.core.v1.EnvVarArgs(
                                        name="PUID",
                                        value="1000",
                                    ),
                                    kubernetes.core.v1.EnvVarArgs(
                                        name="PGID",
                                        value="1000",
                                    ),
                                    kubernetes.core.v1.EnvVarArgs(
                                        name="TZ",
                                        value="UTC",
                                    ),
                                    kubernetes.core.v1.EnvVarArgs(
                                        name="MONGO_USER",
                                        value="unifi",
                                    ),
                                    kubernetes.core.v1.EnvVarArgs(
                                        name="MONGO_PASS",
                                        value="unifi",
                                    ),
                                    kubernetes.core.v1.EnvVarArgs(
                                        name="MONGO_HOST",
                                        value="unifi-db",
                                    ),
                                    kubernetes.core.v1.EnvVarArgs(
                                        name="MONGO_PORT",
                                        value="27017",
                                    ),
                                    kubernetes.core.v1.EnvVarArgs(
                                        name="MONGO_DBNAME",
                                        value="unifi",
                                    ),
                                ],
                                ports=[
                                    kubernetes.core.v1.ContainerPortArgs(
                                        name="https",
                                        container_port=8443,
                                        protocol="TCP",
                                    ),
                                    kubernetes.core.v1.ContainerPortArgs(
                                        name="http",
                                        container_port=8080,
                                        protocol="TCP",
                                    ),
                                    kubernetes.core.v1.ContainerPortArgs(
                                        name="stun",
                                        container_port=3478,
                                        protocol="UDP",
                                    ),
                                    kubernetes.core.v1.ContainerPortArgs(
                                        name="discovery",
                                        container_port=10001,
                                        protocol="UDP",
                                    ),
                                    kubernetes.core.v1.ContainerPortArgs(
                                        name="http-redirect",
                                        container_port=8880,
                                        protocol="TCP",
                                    ),
                                    kubernetes.core.v1.ContainerPortArgs(
                                        name="speedtest",
                                        container_port=6789,
                                        protocol="TCP",
                                    ),
                                    kubernetes.core.v1.ContainerPortArgs(
                                        name="l2-discovery",
                                        container_port=1900,
                                        protocol="UDP",
                                    ),
                                ],
                                volume_mounts=[
                                    kubernetes.core.v1.VolumeMountArgs(
                                        name="unifi-data",
                                        mount_path="/config",
                                    ),
                                ],
                                resources=kubernetes.core.v1.ResourceRequirementsArgs(
                                    requests={
                                        "cpu": "500m",
                                        "memory": "1Gi",
                                    },
                                    limits={
                                        "cpu": "2000m",
                                        "memory": "2Gi",
                                    },
                                ),
                            ),
                        ],
                        volumes=[
                            kubernetes.core.v1.VolumeArgs(
                                name="unifi-data",
                                persistent_volume_claim=kubernetes.core.v1.PersistentVolumeClaimVolumeSourceArgs(
                                    claim_name=unifi_pvc.metadata.name,
                                ),
                            ),
                        ],
                    ),
                ),
            ),
            opts=pulumi.ResourceOptions(parent=self, depends_on=[unifi_pvc, mongodb_service]),
        )

        # Create LoadBalancer Service for UniFi Controller
        unifi_service = kubernetes.core.v1.Service(
            "unifi-controller",
            metadata=kubernetes.meta.v1.ObjectMetaArgs(
                name="unifi-controller",
                namespace=ns.metadata.name,
                annotations={
                    "metallb.universe.tf/loadBalancerIPs": "192.168.1.29"
                },
            ),
            spec=kubernetes.core.v1.ServiceSpecArgs(
                type="LoadBalancer",
                selector={
                    "app": "unifi-controller",
                },
                ports=[
                    kubernetes.core.v1.ServicePortArgs(
                        name="https",
                        port=443,
                        target_port=8443,
                        protocol="TCP",
                    ),
                    kubernetes.core.v1.ServicePortArgs(
                        name="http",
                        port=80,
                        target_port=8080,
                        protocol="TCP",
                    ),
                    kubernetes.core.v1.ServicePortArgs(
                        name="https-alt",
                        port=8443,
                        target_port=8443,
                        protocol="TCP",
                    ),
                    kubernetes.core.v1.ServicePortArgs(
                        name="http-alt",
                        port=8080,
                        target_port=8080,
                        protocol="TCP",
                    ),
                    kubernetes.core.v1.ServicePortArgs(
                        name="http-redirect",
                        port=8880,
                        target_port=8880,
                        protocol="TCP",
                    ),
                    kubernetes.core.v1.ServicePortArgs(
                        name="speedtest",
                        port=6789,
                        target_port=6789,
                        protocol="TCP",
                    ),
                    kubernetes.core.v1.ServicePortArgs(
                        name="stun",
                        port=3478,
                        target_port=3478,
                        protocol="UDP",
                    ),
                    kubernetes.core.v1.ServicePortArgs(
                        name="discovery",
                        port=10001,
                        target_port=10001,
                        protocol="UDP",
                    ),
                    kubernetes.core.v1.ServicePortArgs(
                        name="l2-discovery",
                        port=1900,
                        target_port=1900,
                        protocol="UDP",
                    ),
                ],
            ),
            opts=pulumi.ResourceOptions(parent=self, depends_on=[unifi_deployment]),
        )

        # Store namespace and URL for external reference
        self.namespace = ns.metadata.name
        self.url = "https://192.168.1.49"

        # Export UniFi Controller info
        pulumi.export("unifi_controller_namespace", ns.metadata.name)
        pulumi.export("unifi_controller_url", self.url)
