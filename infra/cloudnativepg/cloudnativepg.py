import pulumi
import pulumi_kubernetes as kubernetes


class CloudNativePG(pulumi.ComponentResource):
    """
    CloudNativePG operator for managing PostgreSQL databases in Kubernetes.
    
    This component installs the CloudNativePG operator which provides:
    - PostgreSQL cluster management
    - High availability and failover
    - Automated backups and point-in-time recovery
    - Declarative configuration
    - Rolling updates
    """
    
    def __init__(self, opts=None):
        # Create namespace for CloudNativePG operator
        ns = kubernetes.core.v1.Namespace(
            "cloudnative-pg",
            metadata=kubernetes.meta.v1.ObjectMetaArgs(
                name="cloudnative-pg",
                labels={
                    "pod-security.kubernetes.io/enforce": "privileged",
                    "pod-security.kubernetes.io/audit": "privileged",
                    "pod-security.kubernetes.io/warn": "privileged",
                },
            ),
        )
        
        super().__init__(
            "custom:CloudNativePG",
            "cloudnative-pg",
            {},
            opts=pulumi.ResourceOptions(parent=ns),
        )

        # Install CloudNativePG operator using Helm
        self.operator = kubernetes.helm.v3.Release(
            "cloudnative-pg",
            name="cloudnative-pg",
            chart="cloudnative-pg",
            version="0.22.1",  # Latest stable version as of Oct 2024
            namespace=ns.metadata.name,
            repository_opts={
                "repo": "https://cloudnative-pg.github.io/charts",
            },
            values={
                # Operator configuration
                "replicaCount": 1,
                
                # Resource limits for the operator
                "resources": {
                    "limits": {
                        "cpu": "500m",
                        "memory": "512Mi"
                    },
                    "requests": {
                        "cpu": "100m",
                        "memory": "128Mi"
                    }
                },
                
                # Monitoring configuration (Prometheus metrics)
                "monitoring": {
                    "enabled": True,
                    "podMonitor": {
                        "enabled": True,
                    }
                },
                
                # Webhook configuration
                "webhook": {
                    "enabled": True,
                    "port": 9443,
                },
                
                # CRD installation
                "crds": {
                    "create": True,
                },
            },
            opts=pulumi.ResourceOptions(parent=self, depends_on=[ns]),
        )
        
        self.namespace = ns.metadata.name
        
        # Register outputs
        self.register_outputs({
            "namespace": self.namespace,
        })

