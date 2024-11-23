import pulumi
import pulumi_kubernetes as kubernetes
from metallb.metal_lb import MetalLb
from ebus.ebusd import Ebusd
from tools.ubuntu import Ubuntu
from cert_manager.cert_manager import CertManager
#from mqtt.emqx import EmqxOperator
#from mqtt.hivemq import HiveMqOperator
from mqtt.mosquitto import Mosquitto

config = pulumi.Config()

metal_lb = MetalLb()

# Create a namespace (user supplies the name of the namespace)
ns = kubernetes.core.v1.Namespace(
    "home-automation",
    metadata=kubernetes.meta.v1.ObjectMetaArgs(
        name="home-automation",
    ),
)

ebusd = Ebusd(ns)
#ubuntu = Ubuntu(ns)
#certManager = CertManager()
#emqx = EmqxOperator(certManager)
#hivemq = HiveMqOperator()
mosquitto = Mosquitto(ns)

