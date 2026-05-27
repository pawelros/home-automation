import pulumi
import pulumi_kubernetes as kubernetes


class ExternalDNS(pulumi.ComponentResource):
    def __init__(self, pihole_url: str, opts=None):
        """
        Deploy external-dns to automatically update DNS records in Pi-hole.
        Uses plain Kubernetes manifests as per official tutorial:
        https://github.com/kubernetes-sigs/external-dns/blob/master/docs/tutorials/pihole.md
        
        Args:
            pihole_url: URL of the Pi-hole server (e.g., "http://192.168.1.3")
            opts: Pulumi resource options
        """
        super().__init__(
            "external-dns",
            "external-dns",
            None,
            opts=opts,
        )
        
        # Get Pulumi config for secrets
        # For Pi-hole v6, use admin password (not API key - API keys are deprecated in v6)
        # We check both pihole_password and pihole_api_key for flexibility
        homepage_config = pulumi.Config('homepage')
        external_dns_config = pulumi.Config('external-dns')
        
        # Prefer dedicated external-dns password, fallback to homepage API key for compatibility
        pihole_password = external_dns_config.get_secret('pihole_password')
        pihole_api_key = homepage_config.get_secret('pihole_api_key')  # Fallback
        
        # Create namespace for external-dns
        ns = kubernetes.core.v1.Namespace(
            "external-dns",
            metadata=kubernetes.meta.v1.ObjectMetaArgs(
                name="external-dns",
            ),
            opts=pulumi.ResourceOptions(parent=self),
        )
        
        # Create secret for Pi-hole password/API key
        # According to official tutorial: https://github.com/kubernetes-sigs/external-dns/blob/master/docs/tutorials/pihole.md
        # The secret key must be EXTERNAL_DNS_PIHOLE_PASSWORD
        # For Pi-hole v6: Use admin password (API keys are deprecated)
        secret = kubernetes.core.v1.Secret(
            "pihole-password",
            metadata=kubernetes.meta.v1.ObjectMetaArgs(
                name="pihole-password",
                namespace=ns.metadata.name,
            ),
            type="Opaque",
            string_data=pulumi.Output.all(pihole_password, pihole_api_key).apply(
                lambda args: {
                    "EXTERNAL_DNS_PIHOLE_PASSWORD": args[0] if args[0] else (args[1] if args[1] else "")
                }
            ),
            opts=pulumi.ResourceOptions(parent=self, depends_on=[ns]),
        )
        
        # ServiceAccount
        service_account = kubernetes.core.v1.ServiceAccount(
            "external-dns",
            metadata=kubernetes.meta.v1.ObjectMetaArgs(
                name="external-dns",
                namespace=ns.metadata.name,
            ),
            opts=pulumi.ResourceOptions(parent=self, depends_on=[ns]),
        )
        
        # ClusterRole
        # Note: If migrating from Helm chart, delete the Helm release first:
        # helm uninstall external-dns -n external-dns
        cluster_role = kubernetes.rbac.v1.ClusterRole(
            "external-dns",
            metadata=kubernetes.meta.v1.ObjectMetaArgs(
                name="external-dns",
            ),
            rules=[
                kubernetes.rbac.v1.PolicyRuleArgs(
                    api_groups=[""],
                    resources=["services", "pods"],
                    verbs=["get", "watch", "list"],
                ),
                kubernetes.rbac.v1.PolicyRuleArgs(
                    api_groups=["discovery.k8s.io"],
                    resources=["endpointslices"],
                    verbs=["get", "watch", "list"],
                ),
                kubernetes.rbac.v1.PolicyRuleArgs(
                    api_groups=["extensions", "networking.k8s.io"],
                    resources=["ingresses"],
                    verbs=["get", "watch", "list"],
                ),
                kubernetes.rbac.v1.PolicyRuleArgs(
                    api_groups=[""],
                    resources=["nodes"],
                    verbs=["list", "watch"],
                ),
            ],
            opts=pulumi.ResourceOptions(
                parent=self,
            ),
        )
        
        # ClusterRoleBinding
        cluster_role_binding = kubernetes.rbac.v1.ClusterRoleBinding(
            "external-dns-viewer",
            metadata=kubernetes.meta.v1.ObjectMetaArgs(
                name="external-dns-viewer",
            ),
            role_ref=kubernetes.rbac.v1.RoleRefArgs(
                api_group="rbac.authorization.k8s.io",
                kind="ClusterRole",
                name="external-dns",
            ),
            subjects=[
                kubernetes.rbac.v1.SubjectArgs(
                    kind="ServiceAccount",
                    name="external-dns",
                    namespace=ns.metadata.name,
                ),
            ],
            opts=pulumi.ResourceOptions(
                parent=self,
                depends_on=[cluster_role, service_account],
            ),
        )
        
        # Deployment
        deployment = kubernetes.apps.v1.Deployment(
            "external-dns",
            metadata=kubernetes.meta.v1.ObjectMetaArgs(
                name="external-dns",
                namespace=ns.metadata.name,
            ),
            spec=kubernetes.apps.v1.DeploymentSpecArgs(
                strategy=kubernetes.apps.v1.DeploymentStrategyArgs(
                    type="Recreate",
                ),
                selector=kubernetes.meta.v1.LabelSelectorArgs(
                    match_labels={
                        "app": "external-dns",
                    },
                ),
                template=kubernetes.core.v1.PodTemplateSpecArgs(
                    metadata=kubernetes.meta.v1.ObjectMetaArgs(
                        labels={
                            "app": "external-dns",
                        },
                    ),
                    spec=kubernetes.core.v1.PodSpecArgs(
                        service_account_name="external-dns",
                        security_context=kubernetes.core.v1.PodSecurityContextArgs(
                            fs_group=65534,  # For ExternalDNS to be able to read Kubernetes token files
                        ),
                        containers=[
                            kubernetes.core.v1.ContainerArgs(
                                name="external-dns",
                                image="registry.k8s.io/external-dns/external-dns:v0.20.0",
                                # Load secret via envFrom as per official tutorial
                                env_from=[
                                    kubernetes.core.v1.EnvFromSourceArgs(
                                        secret_ref=kubernetes.core.v1.SecretEnvSourceArgs(
                                            name="pihole-password",
                                        ),
                                    ),
                                ],
                                args=[
                                    "--source=service",
                                    "--source=ingress",
                                    # Pi-hole only supports A/AAAA/CNAME records so there is no mechanism to track ownership.
                                    # You don't need to set this flag, but if you leave it unset, you will receive warning
                                    # logs when ExternalDNS attempts to create TXT records.
                                    "--registry=noop",
                                    # IMPORTANT: If you have records that you manage manually in Pi-hole, set
                                    # the policy to upsert-only so they do not get deleted.
                                    "--policy=upsert-only",
                                    "--provider=pihole",
                                    "--pihole-api-version=6",
                                    f"--pihole-server={pihole_url}",
                                    "--pihole-tls-skip-verify",
                                    "--log-level=info",
                                    "--log-format=text",
                                    "--interval=1m",
                                ],
                            ),
                        ],
                    ),
                ),
            ),
            opts=pulumi.ResourceOptions(
                parent=self,
                depends_on=[ns, secret, service_account, cluster_role_binding],
            ),
        )
        
        self.namespace = ns.metadata.name
        self.deployment = deployment
        
        # Register outputs
        self.register_outputs({
            "namespace": self.namespace,
        })

