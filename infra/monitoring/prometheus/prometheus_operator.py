import pulumi
import pulumi_kubernetes as kubernetes
from pulumi_kubernetes.helm.v3 import Release, ReleaseArgs, RepositoryOptsArgs


class PrometheusOperator(pulumi.ComponentResource):
    def __init__(self, opts=None):
        super().__init__(
            "prometheus-operator",
            "prometheus-operator",
            None,
        )

        # Create dedicated namespace for Prometheus Operator
        ns = kubernetes.core.v1.Namespace(
            "prometheus",
            metadata=kubernetes.meta.v1.ObjectMetaArgs(
                name="prometheus",
            ),
        )

        # Install minimal Prometheus Operator (CRDs + Operator only)
        prometheus_operator_release = Release(
            "prometheus-operator",
            ReleaseArgs(
                chart="kube-prometheus-stack",
                namespace=ns.metadata.name,
                create_namespace=False,
                atomic=True,
                timeout=300,
                repository_opts=RepositoryOptsArgs(
                    repo="https://prometheus-community.github.io/helm-charts",
                ),
                values={
                    # Disable all components except the operator and CRDs
                    "prometheusOperator": {
                        "enabled": True,
                        "resources": {
                            "requests": {
                                "cpu": "50m",
                                "memory": "64Mi",
                            },
                            "limits": {
                                "cpu": "200m",
                                "memory": "256Mi",
                            },
                        },
                    },
                    
                    # Disable Prometheus server (we don't need it for ServiceMonitor CRDs)
                    "prometheus": {
                        "enabled": False,
                    },
                    
                    # Disable Grafana (we have our own)
                    "grafana": {
                        "enabled": False,
                    },
                    
                    # Disable Alertmanager (not needed for logs)
                    "alertmanager": {
                        "enabled": False,
                    },
                    
                    # Disable node exporter (not needed for logs)
                    "nodeExporter": {
                        "enabled": False,
                    },
                    
                    # Disable kube-state-metrics (not needed for logs)
                    "kubeStateMetrics": {
                        "enabled": False,
                    },
                    
                    # Keep CRDs (this is what we need for ServiceMonitor)
                    "crds": {
                        "enabled": True,
                    },
                    
                    # Disable default rules and service monitors
                    "defaultRules": {
                        "create": False,
                    },
                    
                    # Disable kubelet service monitor
                    "kubelet": {
                        "enabled": False,
                    },
                    
                    # Disable core DNS service monitor
                    "coreDns": {
                        "enabled": False,
                    },
                    
                    # Disable kube controller manager
                    "kubeControllerManager": {
                        "enabled": False,
                    },
                    
                    # Disable kube etcd
                    "kubeEtcd": {
                        "enabled": False,
                    },
                    
                    # Disable kube scheduler
                    "kubeScheduler": {
                        "enabled": False,
                    },
                    
                    # Disable kube proxy
                    "kubeProxy": {
                        "enabled": False,
                    },
                    
                    # Disable kube api server
                    "kubeApiServer": {
                        "enabled": False,
                    },
                },
            ),
            opts=pulumi.ResourceOptions(parent=self, depends_on=[ns]),
        )

        # Export info
        pulumi.export("prometheus_operator_namespace", ns.metadata.name)
        pulumi.export("prometheus_operator_crds_installed", True)
