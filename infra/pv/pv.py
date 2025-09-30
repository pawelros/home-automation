import pulumi
import pulumi_kubernetes as k8s


class Pv(pulumi.ComponentResource):
    def __init__(self, ns: k8s.core.v1.Namespace, opts=None):
        super().__init__(
            "pv",
            "pv",
            None,
        )

        # Define the PersistentVolume
        self.pv_controller_node = k8s.core.v1.PersistentVolume(
            "pv-controller-node",
            metadata=k8s.meta.v1.ObjectMetaArgs(
                name="pv-controller-node",
                namespace=ns,
            ),
            spec=k8s.core.v1.PersistentVolumeSpecArgs(
                storage_class_name="local-storage",
                capacity={"storage": "10Gi"},
                volume_mode="Filesystem",
                persistent_volume_reclaim_policy="Delete",
                access_modes=["ReadWriteOnce"],
                local=k8s.core.v1.LocalVolumeSourceArgs(path="/mnt/pv/"),
                node_affinity=k8s.core.v1.VolumeNodeAffinityArgs(
                    required=k8s.core.v1.NodeSelectorArgs(
                        node_selector_terms=[
                            k8s.core.v1.NodeSelectorTermArgs(
                                match_expressions=[
                                    k8s.core.v1.NodeSelectorRequirementArgs(
                                        key="kubernetes.io/hostname",
                                        operator="In",
                                        values=["k8s-controller"],
                                    ),
                                ],
                            ),
                        ],
                    ),
                ),
            ),
            opts=pulumi.ResourceOptions(parent=self),
        )

        self.pv_node_1 = k8s.core.v1.PersistentVolume(
            "pv-node-1",
            metadata=k8s.meta.v1.ObjectMetaArgs(
                name="pv-node-1",
                namespace=ns,
            ),
            spec=k8s.core.v1.PersistentVolumeSpecArgs(
                storage_class_name="local-storage",
                capacity={"storage": "10Gi"},
                volume_mode="Filesystem",
                persistent_volume_reclaim_policy="Delete",
                access_modes=["ReadWriteOnce"],
                local=k8s.core.v1.LocalVolumeSourceArgs(path="/mnt/pv/"),
                node_affinity=k8s.core.v1.VolumeNodeAffinityArgs(
                    required=k8s.core.v1.NodeSelectorArgs(
                        node_selector_terms=[
                            k8s.core.v1.NodeSelectorTermArgs(
                                match_expressions=[
                                    k8s.core.v1.NodeSelectorRequirementArgs(
                                        key="kubernetes.io/hostname",
                                        operator="In",
                                        values=["k8s-node-1"],
                                    ),
                                ],
                            ),
                        ],
                    ),
                ),
            ),
            opts=pulumi.ResourceOptions(parent=self),
        )

        self.pv_node_2 = k8s.core.v1.PersistentVolume(
            "pv-node-2",
            metadata=k8s.meta.v1.ObjectMetaArgs(
                name="pv-node-2",
                namespace=ns,
            ),
            spec=k8s.core.v1.PersistentVolumeSpecArgs(
                storage_class_name="local-storage",
                capacity={"storage": "10Gi"},
                volume_mode="Filesystem",
                persistent_volume_reclaim_policy="Delete",
                access_modes=["ReadWriteOnce"],
                local=k8s.core.v1.LocalVolumeSourceArgs(path="/mnt/pv/"),
                node_affinity=k8s.core.v1.VolumeNodeAffinityArgs(
                    required=k8s.core.v1.NodeSelectorArgs(
                        node_selector_terms=[
                            k8s.core.v1.NodeSelectorTermArgs(
                                match_expressions=[
                                    k8s.core.v1.NodeSelectorRequirementArgs(
                                        key="kubernetes.io/hostname",
                                        operator="In",
                                        values=["k8s-node-2"],
                                    ),
                                ],
                            ),
                        ],
                    ),
                ),
            ),
            opts=pulumi.ResourceOptions(parent=self),
        )

        # NFS Persistent Volumes for TrueNAS storage
        self.pv_media_nfs = k8s.core.v1.PersistentVolume(
            "pv-media-nfs",
            metadata=k8s.meta.v1.ObjectMetaArgs(
                name="pv-media-nfs",
            ),
            spec=k8s.core.v1.PersistentVolumeSpecArgs(
                storage_class_name="nfs-media",
                capacity={"storage": "1Ti"},
                volume_mode="Filesystem",
                persistent_volume_reclaim_policy="Retain",
                access_modes=["ReadWriteMany"],
                nfs=k8s.core.v1.NFSVolumeSourceArgs(
                    server="192.168.1.127",
                    path="/mnt/SSD/media",
                ),
                mount_options=[
                    "nfsvers=4.1",
                    "rsize=1048576",
                    "wsize=1048576",
                    "hard",
                    "intr",
                    "timeo=600"
                ],
            ),
            opts=pulumi.ResourceOptions(parent=self),
        )

        self.pv_downloads_nfs = k8s.core.v1.PersistentVolume(
            "pv-downloads-nfs",
            metadata=k8s.meta.v1.ObjectMetaArgs(
                name="pv-downloads-nfs",
            ),
            spec=k8s.core.v1.PersistentVolumeSpecArgs(
                storage_class_name="nfs-downloads",
                capacity={"storage": "500Gi"},
                volume_mode="Filesystem",
                persistent_volume_reclaim_policy="Retain",
                access_modes=["ReadWriteMany"],
                nfs=k8s.core.v1.NFSVolumeSourceArgs(
                    server="192.168.1.127",
                    path="/mnt/SSD/downloads",
                ),
                mount_options=[
                    "nfsvers=4.1",
                    "rsize=1048576",
                    "wsize=1048576",
                    "hard",
                    "intr",
                    "timeo=600"
                ],
            ),
            opts=pulumi.ResourceOptions(parent=self),
        )

        # Create PVCs that use the NFS persistent volumes
        self.pvc_media_nfs = k8s.core.v1.PersistentVolumeClaim(
            "arr-media-shared-ssd",
            metadata=k8s.meta.v1.ObjectMetaArgs(
                name="arr-media-shared-ssd",
                namespace="arr-stack",  # Must be in arr-stack namespace
            ),
            spec=k8s.core.v1.PersistentVolumeClaimSpecArgs(
                storage_class_name="nfs-media",
                volume_name=self.pv_media_nfs.metadata["name"],
                access_modes=["ReadWriteMany"],
                resources=k8s.core.v1.ResourceRequirementsArgs(
                    requests={"storage": "1Ti"}
                ),
            ),
            opts=pulumi.ResourceOptions(parent=self),
        )

        self.pvc_downloads_nfs = k8s.core.v1.PersistentVolumeClaim(
            "qbittorrent-downloads-ssd",
            metadata=k8s.meta.v1.ObjectMetaArgs(
                name="qbittorrent-downloads-ssd",
                namespace="arr-stack",  # Must be in arr-stack namespace
            ),
            spec=k8s.core.v1.PersistentVolumeClaimSpecArgs(
                storage_class_name="nfs-downloads",
                volume_name=self.pv_downloads_nfs.metadata["name"],
                access_modes=["ReadWriteMany"],
                resources=k8s.core.v1.ResourceRequirementsArgs(
                    requests={"storage": "500Gi"}
                ),
            ),
            opts=pulumi.ResourceOptions(parent=self),
        )
