import pulumi
import pulumi_kubernetes as kubernetes
from metallb.metal_lb import MetalLb
from pv.pv import Pv
from ebus.ebusd import Ebusd
from tools.ubuntu import Ubuntu
from cert_manager.cert_manager import CertManager

# from mqtt.emqx import EmqxOperator
# from mqtt.hivemq import HiveMqOperator
from istio.istio import Istio
from mqtt.mosquitto import Mosquitto
from kube_metrics_server.metrics_server import MetricsServer
from zigbee2mqtt.zigbee2mqtt import Zigbee2Mqtt
from longhorn.longhorn import Longhorn
from monitoring.grafana.grafana import Grafana
from monitoring.loki.loki import Loki
# from monitoring.prometheus.prometheus_operator import PrometheusOperator
from monitoring.mimir.mimir import Mimir
from monitoring.k8s_monitoring.k8s_monitoring import K8sMonitoring
from minio.minio import MinIO


config = pulumi.Config()

metal_lb = MetalLb()
longhorn = Longhorn()

# Create a namespace (user supplies the name of the namespace)
ns = kubernetes.core.v1.Namespace(
    "home-automation",
    metadata=kubernetes.meta.v1.ObjectMetaArgs(
        name="home-automation",
        labels={"istio-injection": "enabled"},
    ),
)

pv = Pv(ns)
istio = Istio()
# ebusd = Ebusd(ns)
# ubuntu = Ubuntu(ns)
# certManager = CertManager()
# emqx = EmqxOperator(certManager)
# hivemq = HiveMqOperator()
mosquitto = Mosquitto(ns)
metrics_server = MetricsServer()
zigbee2mqtt = Zigbee2Mqtt(ns, pv)
minio = MinIO()
# prometheus_operator = PrometheusOperator()  # Removed - not needed with K8s Monitoring
mimir = Mimir(minio)
loki = Loki(minio)
grafana = Grafana(ns)

# Configure Kubernetes Monitoring to send logs to Loki and metrics to Mimir
k8s_monitoring = K8sMonitoring(
    loki_url="http://loki-gateway.loki.svc.cluster.local",
    mimir_url="http://mimir-nginx.mimir.svc.cluster.local"
)
