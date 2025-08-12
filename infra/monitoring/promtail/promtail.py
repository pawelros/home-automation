import pulumi
import pulumi_kubernetes as kubernetes
from pulumi_kubernetes.helm.v3 import Release, ReleaseArgs, RepositoryOptsArgs


class Promtail(pulumi.ComponentResource):
    def __init__(self, loki=None, opts=None):
        super().__init__(
            "promtail",
            "promtail",
            None,
        )

        # Install Promtail using Helm
        promtail_release = Release(
            "promtail",
            ReleaseArgs(
                chart="promtail",
                namespace="loki",  # Deploy in same namespace as Loki
                create_namespace=False,
                atomic=True,
                timeout=300,
                repository_opts=RepositoryOptsArgs(
                    repo="https://grafana.github.io/helm-charts",
                ),
                values={
                    "config": {
                        "clients": [
                            {
                                "url": "http://loki-gateway/loki/api/v1/push",
                            }
                        ],
                        "snippets": {
                            "scrapeConfigs": """
# Scrape all pod logs
- job_name: kubernetes-pods
  kubernetes_sd_configs:
    - role: pod
  pipeline_stages:
    - cri: {}
  relabel_configs:
    # Only scrape pods that have a log stream
    - source_labels:
        - __meta_kubernetes_pod_controller_name
      regex: ([0-9a-z-.]+?)(-[0-9a-f]{8,10})?
      target_label: __tmp_controller_name
    
    # Scrape all containers
    - source_labels:
        - __meta_kubernetes_pod_container_name
      target_label: container
    
    # Add namespace
    - source_labels:
        - __meta_kubernetes_namespace
      target_label: namespace
    
    # Add pod name
    - source_labels:
        - __meta_kubernetes_pod_name
      target_label: pod
    
    # Add app label if exists
    - source_labels:
        - __meta_kubernetes_pod_label_app
      target_label: app
    
    # Add component label if exists
    - source_labels:
        - __meta_kubernetes_pod_label_component
      target_label: component
    
    # Add controller name
    - source_labels:
        - __tmp_controller_name
      target_label: controller
    
    # Add node name
    - source_labels:
        - __meta_kubernetes_pod_node_name
      target_label: node
    
    # Set the log path
    - source_labels:
        - __meta_kubernetes_pod_uid
        - __meta_kubernetes_pod_container_name
      target_label: __path__
      separator: /
      replacement: /var/log/pods/*$1/*.log
    
    # Drop empty containers
    - source_labels:
        - __meta_kubernetes_pod_container_name
      regex: ^$
      action: drop

# Scrape kubelet logs
- job_name: kubernetes-pods-static
  kubernetes_sd_configs:
    - role: pod
  pipeline_stages:
    - cri: {}
  relabel_configs:
    - source_labels:
        - __meta_kubernetes_pod_annotation_kubernetes_io_config_mirror
      regex: (.+)
      target_label: __tmp_mirrorpod
    - source_labels:
        - __tmp_mirrorpod
      regex: ^$
      action: drop
    - source_labels:
        - __meta_kubernetes_pod_container_name
      target_label: container
    - source_labels:
        - __meta_kubernetes_namespace
      target_label: namespace
    - source_labels:
        - __meta_kubernetes_pod_name
      target_label: pod
    - source_labels:
        - __meta_kubernetes_pod_node_name
      target_label: node
    - source_labels:
        - __meta_kubernetes_pod_uid
        - __meta_kubernetes_pod_container_name
      target_label: __path__
      separator: /
      replacement: /var/log/pods/*$1/*.log

# Scrape host system logs
- job_name: kubernetes-system
  static_configs:
    - targets:
        - localhost
      labels:
        job: kubernetes-system
        __path__: /var/log/syslog
  pipeline_stages:
    - regex:
        expression: '^(?P<timestamp>\\S+\\s+\\S+\\s+\\S+)\\s+(?P<hostname>\\S+)\\s+(?P<service>\\S+)(?:\\[(?P<pid>\\d+)\\])?:\\s*(?P<message>.*)$'
    - labels:
        hostname:
        service:
        pid:
    - timestamp:
        source: timestamp
        format: 'Jan 02 15:04:05'
"""
                        }
                    },
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
                    "tolerations": [
                        {
                            "key": "node-role.kubernetes.io/master",
                            "operator": "Exists",
                            "effect": "NoSchedule",
                        },
                        {
                            "key": "node-role.kubernetes.io/control-plane",
                            "operator": "Exists",
                            "effect": "NoSchedule",
                        },
                    ],
                    "nodeSelector": {},
                    "serviceMonitor": {
                        "enabled": True,
                    },
                    "volumeMounts": [
                        {
                            "name": "varlog",
                            "mountPath": "/var/log",
                            "readOnly": True,
                        },
                        {
                            "name": "varlibdockercontainers",
                            "mountPath": "/var/lib/docker/containers",
                            "readOnly": True,
                        },
                    ],
                    "volumes": [
                        {
                            "name": "varlog",
                            "hostPath": {
                                "path": "/var/log",
                            },
                        },
                        {
                            "name": "varlibdockercontainers",
                            "hostPath": {
                                "path": "/var/lib/docker/containers",
                            },
                        },
                    ],
                    "priorityClassName": "system-node-critical",
                },
            ),
            opts=pulumi.ResourceOptions(parent=self, depends_on=[loki] if loki else []),
        )

        # Export Promtail info
        pulumi.export("promtail_deployed", True)
