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
#from mqtt.mosquitto import Mosquitto
from kube_metrics_server.metrics_server import MetricsServer
#from zigbee2mqtt.zigbee2mqtt import Zigbee2Mqtt
from longhorn.longhorn import Longhorn
from monitoring.grafana.grafana import Grafana
from monitoring.loki.loki import Loki
# from monitoring.prometheus.prometheus_operator import PrometheusOperator
from monitoring.mimir.mimir import Mimir
from monitoring.k8s_monitoring.k8s_monitoring import K8sMonitoring
from monitoring.alloy.alloy import Alloy
from minio.minio import MinIO
from arr_stack.arr_stack import ArrStack
from tailscale.tailscale import Tailscale
from influxdb.influxdb import InfluxDB
from cloudnativepg.cloudnativepg import CloudNativePG
from unifi.unifi_controller import UnifiController


config = pulumi.Config()

metal_lb = MetalLb()
longhorn = Longhorn()
cloudnative_pg = CloudNativePG()

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
#mosquitto = Mosquitto(ns)
metrics_server = MetricsServer()
#zigbee2mqtt = Zigbee2Mqtt(ns, pv)
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

# Deploy Grafana Alloy for scraping Home Assistant metrics
alloy = Alloy(
    mimir_url="http://192.168.1.39",
    loki_url="http://192.168.1.36"
)

# Deploy InfluxDB
influxdb = InfluxDB(ns)

# Deploy PostgreSQL cluster for Home Assistant
home_assistant_postgres = kubernetes.apiextensions.CustomResource(
    "home-assistant-postgres",
    api_version="postgresql.cnpg.io/v1",
    kind="Cluster",
    metadata=kubernetes.meta.v1.ObjectMetaArgs(
        name="home-assistant-postgres",
        namespace=ns.metadata.name,
    ),
    spec={
        "instances": 1,
        "storage": {
            "size": "10Gi",
            "storageClass": "longhorn-ssd",
        },
        "postgresql": {
            "parameters": {
                "max_connections": "100",
                "shared_buffers": "256MB",
            },
        },
        "bootstrap": {
            "initdb": {
                "database": "homeassistant",
                "owner": "homeassistant",
            },
        },
        "monitoring": {
            "enablePodMonitor": True,
        },
    },
    opts=pulumi.ResourceOptions(depends_on=[cloudnative_pg])
)

# Create LoadBalancer service for external access to PostgreSQL
home_assistant_postgres_lb = kubernetes.core.v1.Service(
    "home-assistant-postgres-lb",
    metadata=kubernetes.meta.v1.ObjectMetaArgs(
        name="home-assistant-postgres-lb",
        namespace=ns.metadata.name,
    ),
    spec=kubernetes.core.v1.ServiceSpecArgs(
        type="LoadBalancer",
        ports=[
            kubernetes.core.v1.ServicePortArgs(
                name="postgres",
                port=5432,
                target_port=5432,
                protocol="TCP",
            ),
        ],
        selector={
            "cnpg.io/cluster": "home-assistant-postgres",
            "role": "primary",
        },
        load_balancer_ip="192.168.1.48",
    ),
    opts=pulumi.ResourceOptions(depends_on=[home_assistant_postgres])
)

# Deploy ARR Stack with Jellyfin
arr_stack = ArrStack(
    loki_url="http://loki-gateway.loki.svc.cluster.local", 
    mimir_url="http://mimir-nginx.mimir.svc.cluster.local"
)

# Deploy Tailscale subnet router in its own namespace
tailscale = Tailscale()

# Deploy UniFi Controller
unifi_controller = UnifiController()

# Export ARR Stack URLs (Jellyfin moved to dedicated GPU machine)
# pulumi.export("jellyfin_url", arr_stack.jellyfin_url)  # Now on dedicated GPU machine
pulumi.export("prowlarr_url", arr_stack.prowlarr_url)
pulumi.export("flaresolverr_internal_url", arr_stack.flaresolverr_url)
pulumi.export("jellyseerr_url", arr_stack.jellyseerr_url)
pulumi.export("sonarr_url", arr_stack.sonarr_url)
pulumi.export("radarr_url", arr_stack.radarr_url)
pulumi.export("lidarr_url", arr_stack.lidarr_url)
pulumi.export("qbittorrent_url", arr_stack.qbittorrent_url)
pulumi.export("bazarr_url", arr_stack.bazarr_url)

# Export InfluxDB information
# pulumi.export("influxdb_external_url", influxdb.external_url)
# pulumi.export("influxdb_internal_url", influxdb.internal_url)

# Export Tailscale information
pulumi.export("tailscale_namespace", tailscale.namespace)
pulumi.export("tailscale_connector", tailscale.connector_name)

# Export Home Assistant PostgreSQL connection information
pulumi.export("home_assistant_postgres_host_internal", pulumi.Output.concat("home-assistant-postgres-rw.", ns.metadata.name, ".svc.cluster.local"))
pulumi.export("home_assistant_postgres_host_external", "192.168.1.48")
pulumi.export("home_assistant_postgres_port", "5432")
pulumi.export("home_assistant_postgres_database", "homeassistant")
pulumi.export("home_assistant_postgres_user", "homeassistant")
