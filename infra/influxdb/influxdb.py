import pulumi
import pulumi_kubernetes as kubernetes
from pulumi_kubernetes.helm.v3 import Chart, ChartOpts, FetchOpts


class InfluxDB(pulumi.ComponentResource):
    def __init__(self, ns: kubernetes.core.v1.Namespace, opts=None):
        super().__init__("custom:InfluxDB", "influxdb", {}, opts)
    
        self.influxdb = Chart(
            "influxdb",
            ChartOpts(
                chart="influxdb",
                version="4.12.5",
                namespace=ns.metadata.name,
                fetch_opts=FetchOpts(
                    repo="https://helm.influxdata.com/"
                ),
                values={
                    "image": {
                        "repository": "influxdb",
                        "tag": "1.8.10",
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
                        "port": 8086,
                        "annotations": {
                            "metallb.universe.tf/loadBalancerIPs": "192.168.1.40"
                        }
                    },
                    "setDefaultUser": {
                        "enabled": True,
                        "user": {
                            "username": "admin",
                            "password": "admin123"
                        }
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
                        "path": "/ping",
                        "initialDelaySeconds": 30,
                        "timeoutSeconds": 5,
                        "periodSeconds": 10,
                        "failureThreshold": 3
                    },
                    "readinessProbe": {
                        "path": "/ping",
                        "initialDelaySeconds": 5,
                        "timeoutSeconds": 1,
                        "periodSeconds": 5,
                        "failureThreshold": 3
                    },
                    "config": {
                        "http": {
                            "enabled": True,
                            "bind-address": ":8086",
                            "auth-enabled": True
                        },
                        "data": {
                            "dir": "/var/lib/influxdb"
                        }
                    },
                    "initContainers": {
                        "enabled": False
                    },
                }
            ),
            opts=pulumi.ResourceOptions(parent=self)
        )
        
        # Store the service URL for external access
        self.external_url = pulumi.Output.concat("http://192.168.1.40:8086")
        self.internal_url = pulumi.Output.concat("http://influxdb.", ns.metadata.name, ".svc.cluster.local:8086")
        
        # Register outputs
        self.register_outputs({
            "external_url": self.external_url,
            "internal_url": self.internal_url
        })
