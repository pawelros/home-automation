import pulumi
import pulumi_kubernetes as kubernetes
from ebus.ebusd import Ebusd
from tools.ubuntu import Ubuntu
from cert_manager.cert_manager import CertManager
from mqtt.emqx import EmqxOperator

config = pulumi.Config()

# Create a namespace (user supplies the name of the namespace)
ns = kubernetes.core.v1.Namespace(
    "home-automation",
    metadata=kubernetes.meta.v1.ObjectMetaArgs(
        name="home-automation",
    ),
)

ebusd = Ebusd(ns)
ubuntu = Ubuntu(ns)
certManager = CertManager()
emqx = EmqxOperator(certManager)

