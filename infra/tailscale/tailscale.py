import pulumi
import pulumi_kubernetes as kubernetes


class Tailscale(pulumi.ComponentResource):
    def __init__(self, opts=None):
        super().__init__(
            "tailscale",
            "tailscale",
            None,
            opts=opts,
        )

        # Create dedicated namespace for Tailscale
        tailscale_ns = kubernetes.core.v1.Namespace(
            "tailscale-namespace",
            metadata=kubernetes.meta.v1.ObjectMetaArgs(
                name="tailscale",
                labels={
                    "name": "tailscale",
                    "pod-security.kubernetes.io/enforce": "privileged",
                    "pod-security.kubernetes.io/audit": "privileged", 
                    "pod-security.kubernetes.io/warn": "privileged",
                }
            ),
            opts=pulumi.ResourceOptions(parent=self),
        )

        # Get the Tailscale OAuth credentials from Pulumi config (encrypted)
        config = pulumi.Config()
        tailscale_client_id = config.require_secret("tailscale-oauth-client-id")
        tailscale_client_secret = config.require_secret("tailscale-oauth-client-secret")

        # Create OAuth secret for the operator
        tailscale_oauth_secret = kubernetes.core.v1.Secret(
            "operator-oauth",
            metadata=kubernetes.meta.v1.ObjectMetaArgs(
                name="operator-oauth",
                namespace=tailscale_ns.metadata["name"],
            ),
            type="Opaque",
            string_data={
                "client_id": tailscale_client_id,
                "client_secret": tailscale_client_secret
            },
            opts=pulumi.ResourceOptions(parent=self),
        )

        # Install Tailscale Operator using Helm with auth key configuration
        tailscale_operator = kubernetes.helm.v3.Release(
            "tailscale-operator",
            name="tailscale-operator",
            chart="tailscale-operator",
            version="1.76.1",  # Pin to specific version to prevent auto-upgrades
            namespace=tailscale_ns.metadata["name"],
            repository_opts={
                "repo": "https://pkgs.tailscale.com/helmcharts",
            },
            values={
                "operatorConfig": {
                    "defaultTags": []
                }
            },
            opts=pulumi.ResourceOptions(parent=self, depends_on=[tailscale_oauth_secret]),
        )

        # Create Tailscale Connector for subnet routing
        # Note: Will be created after operator is deployed and CRDs are available
        tailscale_connector = kubernetes.apiextensions.CustomResource(
            "home-subnet-router",
            api_version="tailscale.com/v1alpha1",
            kind="Connector",
            metadata=kubernetes.meta.v1.ObjectMetaArgs(
                name="home-subnet-router",
                namespace=tailscale_ns.metadata["name"],
            ),
            spec={
                "hostname": "home-subnet-router",
                "subnetRouter": {
                    "advertiseRoutes": [
                        "192.168.1.0/24"
                    ]
                },
                "exitNode": True
            },
            opts=pulumi.ResourceOptions(parent=tailscale_operator),
        )

        # Create a service to expose Tailscale metrics (optional)
        tailscale_service = kubernetes.core.v1.Service(
            "tailscale-metrics",
            metadata=kubernetes.meta.v1.ObjectMetaArgs(
                name="tailscale-metrics",
                namespace=tailscale_ns.metadata["name"],
                labels={
                    "app": "tailscale-connector"
                }
            ),
            spec=kubernetes.core.v1.ServiceSpecArgs(
                selector={
                    "app": "connector",
                    "tailscale.com/connector-name": "home-subnet-router"
                },
                ports=[
                    kubernetes.core.v1.ServicePortArgs(
                        name="metrics",
                        port=9001,
                        target_port=9001,
                        protocol="TCP"
                    )
                ],
                type="ClusterIP"
            ),
            opts=pulumi.ResourceOptions(parent=self),
        )

        # Export useful information
        self.connector_name = tailscale_connector.metadata["name"]
        self.namespace = tailscale_ns.metadata["name"]
        self.oauth_secret_name = tailscale_oauth_secret.metadata["name"]
