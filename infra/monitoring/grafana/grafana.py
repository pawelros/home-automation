import pulumi
import pulumi_kubernetes as kubernetes
from pulumi_kubernetes.helm.v3 import Release, ReleaseArgs, RepositoryOptsArgs


class Grafana(pulumi.ComponentResource):
    def __init__(self, ns: kubernetes.core.v1.Namespace, opts=None):
        super().__init__(
            "grafana",
            "grafana",
            None,
            opts=pulumi.ResourceOptions(parent=ns),
        )

        ns = kubernetes.core.v1.Namespace(
            "grafana",
            metadata=kubernetes.meta.v1.ObjectMetaArgs(
                name="grafana",
            ),
        )

        # Install Grafana using Helm
        grafana_release = Release(
            "grafana",
            ReleaseArgs(
                chart="grafana",
                version="8.5.2",  # Pin to specific version to prevent auto-upgrades
                namespace=ns.metadata.name,
                create_namespace=False,
                atomic=True,
                timeout=60,
                repository_opts=RepositoryOptsArgs(
                    repo="https://grafana.github.io/helm-charts",
                ),
                values={
                    "persistence": {
                        "enabled": True,
                        "size": "2Gi",
                        "storageClassName": "longhorn",
                    },
                    "adminPassword": "admin",  # Change this in production
                    "service": {
                        "type": "LoadBalancer",
                        "port": 80,
                        "annotations": {
                            "metallb.universe.tf/loadBalancerIPs": "192.168.1.35"
                        }
                    },
                    "datasources": {
                        "datasources.yaml": {
                            "apiVersion": 1,
                            "datasources": [
                                {
                                    "name": "Mimir",
                                    "type": "prometheus",
                                    "url": "http://mimir-nginx.mimir.svc.cluster.local/prometheus",
                                    "access": "proxy",
                                    "isDefault": True,
                                },
                                {
                                    "name": "Loki",
                                    "type": "loki",
                                    "url": "http://loki-gateway.loki.svc.cluster.local",
                                    "access": "proxy",
                                    "isDefault": False,
                                },
                                {
                                    "name": "Mimir Alertmanager",
                                    "type": "alertmanager",
                                    "url": "http://mimir-nginx.mimir.svc.cluster.local",
                                    "access": "proxy",
                                    "isDefault": False,
                                    "jsonData": {
                                        "implementation": "mimir",
                                        "handleGrafanaManagedAlerts": False,
                                    },
                                }
                            ],
                        }
                    },
                    "dashboardProviders": {
                        "dashboardproviders.yaml": {
                            "apiVersion": 1,
                            "providers": [
                                {
                                    "name": "default",
                                    "orgId": 1,
                                    "folder": "",
                                    "type": "file",
                                    "disableDeletion": False,
                                    "editable": True,
                                    "options": {
                                        "path": "/var/lib/grafana/dashboards/default"
                                    },
                                }
                            ],
                        }
                    },
                    "dashboards": {
                        "default": {
                            "kubernetes-cluster-monitoring": {
                                "gnetId": 315,
                                "revision": 3,
                                "datasource": "Mimir",
                            },
                            "node-exporter": {
                                "gnetId": 1860,
                                "revision": 37,
                                "datasource": "Mimir",
                            },
                        }
                    },
                    # Enable Grafana dashboard sidecar to auto-discover dashboards from ConfigMaps
                    "sidecar": {
                        "dashboards": {
                            "enabled": True,
                            "label": "grafana_dashboard",
                            "labelValue": "1",
                            "folder": "/tmp/dashboards",
                            "searchNamespace": "ALL",
                            "provider": {
                                "foldersFromFilesStructure": True,
                            },
                        },
                    },
                    "grafana.ini": {
                        "server": {
                            "root_url": "http://192.168.1.35/",
                        },
                        "security": {
                            "allow_embedding": True,
                        },
                        "auth.anonymous": {
                            "enabled": True,
                            "org_role": "Viewer",
                        },
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
                },
            ),
            opts=pulumi.ResourceOptions(parent=self),
        )

        # Export Grafana URL
        pulumi.export("grafana_url", "http://192.168.1.35")
        pulumi.export("grafana_admin_user", "admin")
        pulumi.export("grafana_admin_password", "admin")
