import pulumi
import pulumi_kubernetes as kubernetes
import os
import re


class Homepage(pulumi.ComponentResource):
    def __init__(self, opts=None):
        super().__init__(
            "homepage",
            "homepage",
            None,
            opts=opts,
        )
        
        # Get Pulumi config for secrets from 'homepage' namespace
        config = pulumi.Config('homepage')
        
        # Read secrets from Pulumi config (optional - widgets disabled if not set)
        # Get secrets as Outputs, handling None values
        def get_secret_or_empty(key):
            """Get secret value or empty string if not set"""
            secret = config.get_secret(key)
            return secret if secret is not None else pulumi.Output.from_input('')
        
        secrets = {
            'JELLYFIN_API_KEY': get_secret_or_empty('jellyfin_api_key'),
            'JELLYSEERR_API_KEY': get_secret_or_empty('jellyseerr_api_key'),
            'BAZARR_API_KEY': get_secret_or_empty('bazarr_api_key'),
            'PROWLARR_API_KEY': get_secret_or_empty('prowlarr_api_key'),
            'SONARR_API_KEY': get_secret_or_empty('sonarr_api_key'),
            'RADARR_API_KEY': get_secret_or_empty('radarr_api_key'),
            'LIDARR_API_KEY': get_secret_or_empty('lidarr_api_key'),
            'QBITTORRENT_USERNAME': config.get_secret('qbittorrent_username') or pulumi.Output.from_input('admin'),
            'QBITTORRENT_PASSWORD': get_secret_or_empty('qbittorrent_password'),
            'GRAFANA_USERNAME': get_secret_or_empty('grafana_username'),
            'GRAFANA_PASSWORD': get_secret_or_empty('grafana_password'),
            'UNIFI_USERNAME': get_secret_or_empty('unifi_username'),
            'UNIFI_PASSWORD': get_secret_or_empty('unifi_password'),
            'PROXMOX_USERNAME': get_secret_or_empty('proxmox_username'),
            'PROXMOX_API_TOKEN': get_secret_or_empty('proxmox_api_token'),
            'TRUENAS_API_KEY': get_secret_or_empty('truenas_api_key'),
            'PIHOLE_API_KEY': get_secret_or_empty('pihole_api_key'),
            'HOMEASSISTANT_TOKEN': get_secret_or_empty('homeassistant_token'),
            'TAILSCALE_DEVICE_ID': get_secret_or_empty('tailscale_device_id'),
            'TAILSCALE_API_KEY': get_secret_or_empty('tailscale_api_key'),
        }
        
        # Get the directory where this file is located
        config_dir = os.path.join(os.path.dirname(__file__), 'config')
        
        # Read configuration files
        def read_config_file(filename):
            filepath = os.path.join(config_dir, filename)
            with open(filepath, 'r') as f:
                return f.read()
        
        def substitute_secrets(content, secrets_dict):
            """Replace ${VAR} placeholders with actual secret values"""
            def replacer(match):
                key = match.group(1)
                # Return the secret value, handle None, or empty string if not set
                value = secrets_dict.get(key, '')
                return str(value) if value is not None else ''
            
            return re.sub(r'\$\{([A-Z_]+)\}', replacer, content)
        
        # Read configuration files
        kubernetes_config = read_config_file('kubernetes.yaml')
        settings_config = read_config_file('settings.yaml')
        services_config_template = read_config_file('services.yaml')
        widgets_config = read_config_file('widgets.yaml')
        bookmarks_config = read_config_file('bookmarks.yaml')
        docker_config = read_config_file('docker.yaml')
        custom_css = read_config_file('custom.css')
        custom_js = read_config_file('custom.js')
        
        # Substitute secrets in services config
        # This needs to be done with pulumi.Output.all to handle secret values
        services_config = pulumi.Output.all(**secrets).apply(
            lambda s: substitute_secrets(services_config_template, s)
        )
        
        # Create a hash of all config files to force pod restart on config changes
        import hashlib
        config_hash = pulumi.Output.all(
            kubernetes_config,
            settings_config,
            services_config,
            widgets_config,
            bookmarks_config,
        ).apply(lambda configs: hashlib.sha256(''.join(configs).encode()).hexdigest()[:8])

        # Create dedicated namespace for Homepage
        ns = kubernetes.core.v1.Namespace(
            "homepage",
            metadata=kubernetes.meta.v1.ObjectMetaArgs(
                name="homepage",
            ),
            opts=pulumi.ResourceOptions(parent=self),
        )

        # ServiceAccount
        service_account = kubernetes.core.v1.ServiceAccount(
            "homepage",
            metadata=kubernetes.meta.v1.ObjectMetaArgs(
                name="homepage",
                namespace=ns.metadata.name,
                labels={
                    "app.kubernetes.io/name": "homepage",
                },
            ),
            opts=pulumi.ResourceOptions(parent=self, depends_on=[ns]),
        )

        # Secret for ServiceAccount token
        secret = kubernetes.core.v1.Secret(
            "homepage",
            type="kubernetes.io/service-account-token",
            metadata=kubernetes.meta.v1.ObjectMetaArgs(
                name="homepage",
                namespace=ns.metadata.name,
                labels={
                    "app.kubernetes.io/name": "homepage",
                },
                annotations={
                    "kubernetes.io/service-account.name": "homepage",
                },
            ),
            opts=pulumi.ResourceOptions(parent=self, depends_on=[service_account]),
        )

        # ConfigMap with comprehensive configuration
        config_map = kubernetes.core.v1.ConfigMap(
            "homepage",
            metadata=kubernetes.meta.v1.ObjectMetaArgs(
                name="homepage",
                namespace=ns.metadata.name,
                labels={
                    "app.kubernetes.io/name": "homepage",
                },
                annotations=pulumi.Output.all(config_hash).apply(
                    lambda h: {"homepage/config-version": h[0]}
                ),
            ),
            data=pulumi.Output.all(
                kubernetes=kubernetes_config,
                settings=settings_config,
                services=services_config,
                widgets=widgets_config,
                bookmarks=bookmarks_config,
                docker=docker_config,
                css=custom_css,
                js=custom_js,
            ).apply(lambda d: {
                "kubernetes.yaml": d['kubernetes'],
                "settings.yaml": d['settings'],
                "services.yaml": d['services'],
                "widgets.yaml": d['widgets'],
                "bookmarks.yaml": d['bookmarks'],
                "docker.yaml": d['docker'],
                "custom.css": d['css'],
                "custom.js": d['js'],
            }),
            opts=pulumi.ResourceOptions(parent=self, depends_on=[ns]),
        )

        # ClusterRole
        cluster_role = kubernetes.rbac.v1.ClusterRole(
            "homepage",
            metadata=kubernetes.meta.v1.ObjectMetaArgs(
                name="homepage",
                labels={
                    "app.kubernetes.io/name": "homepage",
                },
            ),
            rules=[
                kubernetes.rbac.v1.PolicyRuleArgs(
                    api_groups=[""],
                    resources=["namespaces", "pods", "nodes"],
                    verbs=["get", "list"],
                ),
                kubernetes.rbac.v1.PolicyRuleArgs(
                    api_groups=["extensions", "networking.k8s.io"],
                    resources=["ingresses"],
                    verbs=["get", "list"],
                ),
                kubernetes.rbac.v1.PolicyRuleArgs(
                    api_groups=["traefik.io"],
                    resources=["ingressroutes"],
                    verbs=["get", "list"],
                ),
                kubernetes.rbac.v1.PolicyRuleArgs(
                    api_groups=["gateway.networking.k8s.io"],
                    resources=["httproutes", "gateways"],
                    verbs=["get", "list"],
                ),
                kubernetes.rbac.v1.PolicyRuleArgs(
                    api_groups=["metrics.k8s.io"],
                    resources=["nodes", "pods"],
                    verbs=["get", "list"],
                ),
            ],
            opts=pulumi.ResourceOptions(parent=self),
        )

        # ClusterRoleBinding
        cluster_role_binding = kubernetes.rbac.v1.ClusterRoleBinding(
            "homepage",
            metadata=kubernetes.meta.v1.ObjectMetaArgs(
                name="homepage",
                labels={
                    "app.kubernetes.io/name": "homepage",
                },
            ),
            role_ref=kubernetes.rbac.v1.RoleRefArgs(
                api_group="rbac.authorization.k8s.io",
                kind="ClusterRole",
                name="homepage",
            ),
            subjects=[
                kubernetes.rbac.v1.SubjectArgs(
                    kind="ServiceAccount",
                    name="homepage",
                    namespace=ns.metadata.name,
                ),
            ],
            opts=pulumi.ResourceOptions(parent=self, depends_on=[cluster_role, service_account]),
        )

        # Service
        service = kubernetes.core.v1.Service(
            "homepage",
            metadata=kubernetes.meta.v1.ObjectMetaArgs(
                name="homepage",
                namespace=ns.metadata.name,
                labels={
                    "app.kubernetes.io/name": "homepage",
                },
                annotations={
                    "metallb.universe.tf/loadBalancerIPs": "192.168.1.50",
                    "external-dns.alpha.kubernetes.io/hostname": "homepage.lab"
                },
            ),
            spec=kubernetes.core.v1.ServiceSpecArgs(
                type="LoadBalancer",
                ports=[
                    kubernetes.core.v1.ServicePortArgs(
                        port=80,
                        target_port=3000,
                        protocol="TCP",
                        name="http",
                    ),
                ],
                selector={
                    "app.kubernetes.io/name": "homepage",
                },
            ),
            opts=pulumi.ResourceOptions(parent=self, depends_on=[ns]),
        )

        # Deployment
        deployment = kubernetes.apps.v1.Deployment(
            "homepage",
            metadata=kubernetes.meta.v1.ObjectMetaArgs(
                name="homepage",
                namespace=ns.metadata.name,
                labels={
                    "app.kubernetes.io/name": "homepage",
                },
            ),
            spec=kubernetes.apps.v1.DeploymentSpecArgs(
                revision_history_limit=3,
                replicas=1,
                strategy=kubernetes.apps.v1.DeploymentStrategyArgs(
                    type="RollingUpdate",
                ),
                selector=kubernetes.meta.v1.LabelSelectorArgs(
                    match_labels={
                        "app.kubernetes.io/name": "homepage",
                    },
                ),
                template=kubernetes.core.v1.PodTemplateSpecArgs(
                    metadata=kubernetes.meta.v1.ObjectMetaArgs(
                        labels={
                            "app.kubernetes.io/name": "homepage",
                        },
                        annotations=pulumi.Output.all(config_hash).apply(
                            lambda h: {"homepage/config-hash": h[0]}
                        ),
                    ),
                    spec=kubernetes.core.v1.PodSpecArgs(
                        service_account_name="homepage",
                        automount_service_account_token=True,
                        dns_policy="ClusterFirst",
                        enable_service_links=True,
                        containers=[
                            kubernetes.core.v1.ContainerArgs(
                                name="homepage",
                                image="ghcr.io/gethomepage/homepage:latest",
                                image_pull_policy="Always",
                                env=[
                                    kubernetes.core.v1.EnvVarArgs(
                                        name="HOMEPAGE_ALLOWED_HOSTS",
                                        value="192.168.1.50,homepage,homepage.homepage.svc.cluster.local,localhost",
                                    ),
                                    kubernetes.core.v1.EnvVarArgs(
                                        name="LOG_LEVEL",
                                        value="debug",
                                    ),
                                ],
                                ports=[
                                    kubernetes.core.v1.ContainerPortArgs(
                                        name="http",
                                        container_port=3000,
                                        protocol="TCP",
                                    ),
                                ],
                                volume_mounts=[
                                    kubernetes.core.v1.VolumeMountArgs(
                                        mount_path="/app/config/custom.js",
                                        name="homepage-config",
                                        sub_path="custom.js",
                                    ),
                                    kubernetes.core.v1.VolumeMountArgs(
                                        mount_path="/app/config/custom.css",
                                        name="homepage-config",
                                        sub_path="custom.css",
                                    ),
                                    kubernetes.core.v1.VolumeMountArgs(
                                        mount_path="/app/config/bookmarks.yaml",
                                        name="homepage-config",
                                        sub_path="bookmarks.yaml",
                                    ),
                                    kubernetes.core.v1.VolumeMountArgs(
                                        mount_path="/app/config/docker.yaml",
                                        name="homepage-config",
                                        sub_path="docker.yaml",
                                    ),
                                    kubernetes.core.v1.VolumeMountArgs(
                                        mount_path="/app/config/kubernetes.yaml",
                                        name="homepage-config",
                                        sub_path="kubernetes.yaml",
                                    ),
                                    kubernetes.core.v1.VolumeMountArgs(
                                        mount_path="/app/config/services.yaml",
                                        name="homepage-config",
                                        sub_path="services.yaml",
                                    ),
                                    kubernetes.core.v1.VolumeMountArgs(
                                        mount_path="/app/config/settings.yaml",
                                        name="homepage-config",
                                        sub_path="settings.yaml",
                                    ),
                                    kubernetes.core.v1.VolumeMountArgs(
                                        mount_path="/app/config/widgets.yaml",
                                        name="homepage-config",
                                        sub_path="widgets.yaml",
                                    ),
                                    kubernetes.core.v1.VolumeMountArgs(
                                        mount_path="/app/config/logs",
                                        name="logs",
                                    ),
                                ],
                                resources=kubernetes.core.v1.ResourceRequirementsArgs(
                                    requests={
                                        "cpu": "100m",
                                        "memory": "128Mi",
                                    },
                                    limits={
                                        "cpu": "500m",
                                        "memory": "512Mi",
                                    },
                                ),
                            ),
                        ],
                        volumes=[
                            kubernetes.core.v1.VolumeArgs(
                                name="homepage-config",
                                config_map=kubernetes.core.v1.ConfigMapVolumeSourceArgs(
                                    name="homepage",
                                ),
                            ),
                            kubernetes.core.v1.VolumeArgs(
                                name="logs",
                                empty_dir=kubernetes.core.v1.EmptyDirVolumeSourceArgs(),
                            ),
                        ],
                    ),
                ),
            ),
            opts=pulumi.ResourceOptions(
                parent=self,
                depends_on=[config_map, service_account, cluster_role_binding],
            ),
        )

        # Store references
        self.namespace = ns.metadata.name
        self.url = "http://192.168.1.50"

        # Export Homepage info
        pulumi.export("homepage_namespace", ns.metadata.name)
        pulumi.export("homepage_url", self.url)

