import pulumi
import pulumi_kubernetes as kubernetes
from pulumi_kubernetes.helm.v3 import Release, ReleaseArgs, RepositoryOptsArgs


class Alloy(pulumi.ComponentResource):
    def __init__(self, mimir_url: str, loki_url: str, opts=None):
        super().__init__(
            "alloy",
            "alloy",
            None,
        )
        
        # Get Home Assistant token from Pulumi config (secret)
        config = pulumi.Config()
        ha_token = config.require_secret("home-assistant-token")
        ha_address = config.get("home-assistant-address") or "homeassistant.local:8123"

        # Create dedicated namespace for Alloy
        ns = kubernetes.core.v1.Namespace(
            "grafana-alloy",
            metadata=kubernetes.meta.v1.ObjectMetaArgs(
                name="grafana-alloy",
            ),
        )

        # Alloy configuration for scraping Home Assistant and sending to Mimir/Loki
        alloy_config = pulumi.Output.all(ha_address).apply(lambda args: f"""
// Prometheus scrape configuration for Home Assistant
prometheus.scrape "home_assistant" {{
  targets = [
    {{
      "__address__" = "{args[0]}",
      "job"        = "home-assistant",
    }},
  ]
  
  forward_to = [prometheus.remote_write.mimir.receiver]
  
  scrape_interval = "60s"
  scrape_timeout  = "30s"
  metrics_path    = "/api/prometheus"
  
  // Add bearer token for authentication
  bearer_token_file = "/etc/alloy/secrets/ha-token"
}}

// Remote write to Mimir
prometheus.remote_write "mimir" {{
  endpoint {{
    url = "http://192.168.1.39/api/v1/push"
    
    queue_config {{
      capacity             = 10000
      max_shards          = 10
      min_shards          = 1
      max_samples_per_send = 5000
      batch_send_deadline  = "5s"
    }}
  }}
}}

// Optional: Loki logging (for Alloy's own logs)
loki.write "loki" {{
  endpoint {{
    url = "http://192.168.1.36/loki/api/v1/push"
  }}
  
  external_labels = {{
    cluster = "home-automation",
    job     = "alloy",
  }}
}}

// Self-monitoring - send Alloy's own metrics to Mimir
prometheus.exporter.self "alloy" {{}}

prometheus.scrape "alloy" {{
  targets    = prometheus.exporter.self.alloy.targets
  forward_to = [prometheus.remote_write.mimir.receiver]
}}

// Log Alloy's own logs to Loki
loki.source.api "alloy_logs" {{
  http {{
    listen_address = "0.0.0.0"
    listen_port    = 9999
  }}
  
  forward_to = [loki.write.loki.receiver]
  
  labels = {{
    job = "alloy-logs",
  }}
}}
""")

        # Create ConfigMap with Alloy configuration
        alloy_configmap = kubernetes.core.v1.ConfigMap(
            "alloy-config",
            metadata=kubernetes.meta.v1.ObjectMetaArgs(
                name="alloy-config",
                namespace=ns.metadata.name,
            ),
            data={
                "config.alloy": alloy_config,
            },
            opts=pulumi.ResourceOptions(parent=self, depends_on=[ns])
        )

        # Create Secret for Home Assistant token from Pulumi config
        ha_token_secret = kubernetes.core.v1.Secret(
            "alloy-ha-token",
            metadata=kubernetes.meta.v1.ObjectMetaArgs(
                name="alloy-ha-token",
                namespace=ns.metadata.name,
            ),
            string_data={
                "ha-token": ha_token,
            },
            opts=pulumi.ResourceOptions(parent=self, depends_on=[ns])
        )

        # Install Grafana Alloy using Helm
        alloy_release = Release(
            "alloy",
            ReleaseArgs(
                chart="alloy",
                version="0.9.2",  # Latest stable version
                namespace=ns.metadata.name,
                create_namespace=False,
                atomic=True,
                timeout=300,
                repository_opts=RepositoryOptsArgs(
                    repo="https://grafana.github.io/helm-charts",
                ),
                values={
                    "fullnameOverride": "alloy",
                    
                    # Alloy configuration
                    "alloy": {
                        "configMap": {
                            "create": False,
                            "name": alloy_configmap.metadata.name,
                            "key": "config.alloy",
                        },
                        "extraPorts": [
                            {
                                "name": "loki-api",
                                "port": 9999,
                                "targetPort": 9999,
                                "protocol": "TCP",
                            },
                        ],
                        "mounts": {
                            "extra": [
                                {
                                    "name": "ha-token",
                                    "mountPath": "/etc/alloy/secrets",
                                    "readOnly": True,
                                },
                            ],
                        },
                    },
                    
                    # Controller configuration
                    "controller": {
                        "type": "deployment",
                        "replicas": 1,
                        "volumes": {
                            "extra": [
                                {
                                    "name": "ha-token",
                                    "secret": {
                                        "secretName": ha_token_secret.metadata.name,
                                    },
                                },
                            ],
                        },
                    },
                    
                    # Resources
                    "resources": {
                        "requests": {
                            "cpu": "100m",
                            "memory": "128Mi",
                        },
                        "limits": {
                            "cpu": "500m",
                            "memory": "512Mi",
                        },
                    },
                    
                    # Service Monitor for self-monitoring
                    "serviceMonitor": {
                        "enabled": False,
                    },
                },
            ),
            opts=pulumi.ResourceOptions(parent=self, depends_on=[ns, alloy_configmap, ha_token_secret]),
        )

        # Export Alloy info
        pulumi.export("alloy_namespace", ns.metadata.name)
        pulumi.export("alloy_ha_address", ha_address)

