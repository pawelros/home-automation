import pulumi
import pulumi_kubernetes as kubernetes
from pulumi_kubernetes.helm.v3 import Chart, ChartOpts, FetchOpts


class InfluxDB(pulumi.ComponentResource):
    def __init__(self, ns: kubernetes.core.v1.Namespace, opts=None):
        super().__init__("custom:InfluxDB", "influxdb", {}, opts)
        
        # Get credentials from Pulumi config (secrets)
        config = pulumi.Config()
        admin_password = config.require_secret("influxdb-admin-password")
        admin_token = config.require_secret("influxdb-admin-token")
        
        # Create Kubernetes Secret for InfluxDB credentials
        auth_secret = kubernetes.core.v1.Secret(
            "influxdb-auth",
            metadata=kubernetes.meta.v1.ObjectMetaArgs(
                name="influxdb-auth",
                namespace=ns.metadata.name,
            ),
            string_data={
                "admin-password": admin_password,
                "admin-token": admin_token,
            },
            opts=pulumi.ResourceOptions(parent=self)
        )
    
        self.influxdb = Chart(
            "influxdb",
            ChartOpts(
                chart="influxdb2",
                version="2.1.2",
                namespace=ns.metadata.name,
                fetch_opts=FetchOpts(
                    repo="https://helm.influxdata.com/"
                ),
                values={
                    "fullnameOverride": "influxdb",
                    "image": {
                        "repository": "influxdb",
                        "tag": "2.7.10",
                        "pullPolicy": "IfNotPresent"
                    },
                    "persistence": {
                        "enabled": True,
                        "storageClass": "longhorn-ssd",
                        "size": "20Gi",
                        "accessMode": "ReadWriteOnce"
                    },
                    "service": {
                        "type": "LoadBalancer",
                        "port": 80,
                        "targetPort": 8086,
                        "annotations": {
                            "metallb.universe.tf/loadBalancerIPs": "192.168.1.40"
                        }
                    },
                    "adminUser": {
                        "organization": "home_assistant",
                        "bucket": "home_assistant",
                        "user": "admin",
                        "existingSecret": auth_secret.metadata.name,
                    },
                    "resources": {
                        "requests": {
                            "cpu": "200m",
                            "memory": "512Mi"
                        },
                        "limits": {
                            "cpu": "1000m",
                            "memory": "2Gi"
                        }
                    },
                    "ingress": {
                        "enabled": False  # Use LoadBalancer instead
                    },
                    "livenessProbe": {
                        "path": "/health",
                        "initialDelaySeconds": 30,
                        "timeoutSeconds": 5,
                        "periodSeconds": 10,
                        "failureThreshold": 3
                    },
                    "readinessProbe": {
                        "path": "/health",
                        "initialDelaySeconds": 5,
                        "timeoutSeconds": 1,
                        "periodSeconds": 5,
                        "failureThreshold": 3
                    },
                }
            ),
            opts=pulumi.ResourceOptions(parent=self, depends_on=[auth_secret])
        )
        
        # Store the service URL for external access
        self.external_url = pulumi.Output.concat("http://192.168.1.40")
        self.internal_url = pulumi.Output.concat("http://influxdb.", ns.metadata.name, ".svc.cluster.local:8086")
        
        # Register outputs
        self.register_outputs({
            "external_url": self.external_url,
            "internal_url": self.internal_url
        })
