import os
import pulumi
import pulumi_kubernetes as kubernetes


class MDNS(pulumi.ComponentResource):
    def __init__(self, opts=None):
        """
        Deploy mDNS publisher to make Kubernetes LoadBalancer services discoverable via mDNS.
        
        This creates a Deployment that watches Kubernetes services and publishes them via mDNS
        using the zeroconf library. Services are automatically published if they:
        1. Are of type LoadBalancer
        2. Have a LoadBalancer IP assigned
        3. Have the annotation 'mdns.alpha.kubernetes.io/publish: "true"' OR
           have the annotation 'external-dns.alpha.kubernetes.io/hostname' (auto-publish)
        
        Services will be published as {hostname}.local where hostname comes from:
        - mdns.alpha.kubernetes.io/hostname annotation (preferred)
        - external-dns.alpha.kubernetes.io/hostname annotation (fallback)
        - service-name.local (default)
        
        Args:
            opts: Pulumi resource options
        """
        super().__init__(
            "mdns",
            "mdns",
            None,
            opts=opts,
        )
        
        # Create namespace for mDNS
        ns = kubernetes.core.v1.Namespace(
            "mdns",
            metadata=kubernetes.meta.v1.ObjectMetaArgs(
                name="mdns",
            ),
            opts=pulumi.ResourceOptions(parent=self),
        )
        
        # ServiceAccount
        service_account = kubernetes.core.v1.ServiceAccount(
            "mdns-publisher",
            metadata=kubernetes.meta.v1.ObjectMetaArgs(
                name="mdns-publisher",
                namespace=ns.metadata.name,
            ),
            opts=pulumi.ResourceOptions(parent=self, depends_on=[ns]),
        )
        
        # ClusterRole - needs to watch services
        cluster_role = kubernetes.rbac.v1.ClusterRole(
            "mdns-publisher",
            metadata=kubernetes.meta.v1.ObjectMetaArgs(
                name="mdns-publisher",
            ),
            rules=[
                kubernetes.rbac.v1.PolicyRuleArgs(
                    api_groups=[""],
                    resources=["services"],
                    verbs=["get", "watch", "list"],
                ),
            ],
            opts=pulumi.ResourceOptions(parent=self),
        )
        
        # ClusterRoleBinding
        cluster_role_binding = kubernetes.rbac.v1.ClusterRoleBinding(
            "mdns-publisher",
            metadata=kubernetes.meta.v1.ObjectMetaArgs(
                name="mdns-publisher",
            ),
            role_ref=kubernetes.rbac.v1.RoleRefArgs(
                api_group="rbac.authorization.k8s.io",
                kind="ClusterRole",
                name="mdns-publisher",
            ),
            subjects=[
                kubernetes.rbac.v1.SubjectArgs(
                    kind="ServiceAccount",
                    name="mdns-publisher",
                    namespace=ns.metadata.name,
                ),
            ],
            opts=pulumi.ResourceOptions(
                parent=self,
                depends_on=[cluster_role, service_account],
            ),
        )
        
        # Read the Python script file
        script_path = os.path.join(os.path.dirname(__file__), "mdns_publisher.py")
        with open(script_path, "r") as f:
            script_content = f.read()
        
        # Create ConfigMap with the Python script
        config_map = kubernetes.core.v1.ConfigMap(
            "mdns-publisher-script",
            metadata=kubernetes.meta.v1.ObjectMetaArgs(
                name="mdns-publisher-script",
                namespace=ns.metadata.name,
            ),
            data={
                "mdns_publisher.py": script_content,
            },
            opts=pulumi.ResourceOptions(
                parent=self,
                depends_on=[ns],
            ),
        )
        
        # Deployment that watches Kubernetes services and publishes them via mDNS
        # Uses hostNetwork to access the node's network interface for mDNS broadcasting
        deployment = kubernetes.apps.v1.Deployment(
            "mdns-publisher",
            metadata=kubernetes.meta.v1.ObjectMetaArgs(
                name="mdns-publisher",
                namespace=ns.metadata.name,
            ),
            spec=kubernetes.apps.v1.DeploymentSpecArgs(
                replicas=1,
                selector=kubernetes.meta.v1.LabelSelectorArgs(
                    match_labels={
                        "app": "mdns-publisher",
                    },
                ),
                template=kubernetes.core.v1.PodTemplateSpecArgs(
                    metadata=kubernetes.meta.v1.ObjectMetaArgs(
                        labels={
                            "app": "mdns-publisher",
                        },
                    ),
                    spec=kubernetes.core.v1.PodSpecArgs(
                        service_account_name="mdns-publisher",
                        host_network=True,  # Required for mDNS broadcasting
                        dns_policy="ClusterFirstWithHostNet",
                        containers=[
                            kubernetes.core.v1.ContainerArgs(
                                name="mdns-publisher",
                                image="python:3.11-slim",
                                command=["/bin/sh"],
                                args=[
                                    "-c",
                                    "pip install -q kubernetes zeroconf && python /app/mdns_publisher.py",
                                ],
                                volume_mounts=[
                                    kubernetes.core.v1.VolumeMountArgs(
                                        name="mdns-script",
                                        mount_path="/app",
                                        read_only=True,
                                    ),
                                ],
                            ),
                        ],
                        volumes=[
                            kubernetes.core.v1.VolumeArgs(
                                name="mdns-script",
                                config_map=kubernetes.core.v1.ConfigMapVolumeSourceArgs(
                                    name=config_map.metadata.name,
                                ),
                            ),
                        ],
                    ),
                ),
            ),
            opts=pulumi.ResourceOptions(
                parent=self,
                depends_on=[ns, service_account, cluster_role_binding, config_map],
            ),
        )
        
        self.namespace = ns.metadata.name
        self.deployment = deployment
        
        # Register outputs
        self.register_outputs({
            "namespace": self.namespace,
        })

