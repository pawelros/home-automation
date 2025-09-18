import pulumi
import pulumi_kubernetes as kubernetes
from pulumi_kubernetes.helm.v3 import Release, ReleaseArgs, RepositoryOptsArgs
from .jellyfin import Jellyfin
from .prowlarr import Prowlarr
from .flaresolverr import FlareSolverr
from .jellyseerr import Jellyseerr
from .sonarr import Sonarr


class ArrStack(pulumi.ComponentResource):
    def __init__(self, loki_url: str, mimir_url: str, opts=None):
        super().__init__(
            "arr-stack",
            "arr-stack",
            None,
            opts=opts,
        )

        # Create arr-stack namespace
        arr_stack_ns = kubernetes.core.v1.Namespace(
            "arr-stack",
            metadata=kubernetes.meta.v1.ObjectMetaArgs(
                name="arr-stack",
            ),
            opts=pulumi.ResourceOptions(parent=self),
        )

        # Deploy Jellyfin
        jellyfin = Jellyfin(
            namespace=arr_stack_ns,
            opts=pulumi.ResourceOptions(parent=self)
        )

        # Deploy Prowlarr
        prowlarr = Prowlarr(
            namespace=arr_stack_ns,
            opts=pulumi.ResourceOptions(parent=self)
        )

        # Deploy FlareSolverr
        flaresolverr = FlareSolverr(
            namespace=arr_stack_ns,
            opts=pulumi.ResourceOptions(parent=self)
        )

        # Deploy Jellyseerr
        jellyseerr = Jellyseerr(
            namespace=arr_stack_ns,
            opts=pulumi.ResourceOptions(parent=self)
        )

        # Deploy Sonarr
        sonarr = Sonarr(
            namespace=arr_stack_ns,
            opts=pulumi.ResourceOptions(parent=self)
        )

        # Store references
        self.namespace = arr_stack_ns
        self.jellyfin = jellyfin
        self.prowlarr = prowlarr
        self.flaresolverr = flaresolverr
        self.jellyseerr = jellyseerr
        self.sonarr = sonarr

        # Export useful information
        self.jellyfin_url = jellyfin.web_url
        self.prowlarr_url = prowlarr.web_url
        self.flaresolverr_url = flaresolverr.internal_url
        self.jellyseerr_url = jellyseerr.web_url
        self.sonarr_url = sonarr.web_url
