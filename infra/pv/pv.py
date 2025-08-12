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
