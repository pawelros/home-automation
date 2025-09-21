import pulumi
import pulumi_kubernetes as kubernetes
from pulumi_kubernetes.helm.v3 import Release, ReleaseArgs, RepositoryOptsArgs
# from .jellyfin import Jellyfin  # Moved to dedicated GPU machine
from .prowlarr import Prowlarr
from .flaresolverr import FlareSolverr
from .jellyseerr import Jellyseerr
from .sonarr import Sonarr
from .qbittorrent import QBittorrent
from .bazarr import Bazarr


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

        # Jellyfin moved to dedicated GPU machine
        # jellyfin = Jellyfin(
        #     namespace=arr_stack_ns,
        #     opts=pulumi.ResourceOptions(parent=self)
        # )

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

        # Deploy qBittorrent
        qbittorrent = QBittorrent(
            namespace=arr_stack_ns,
            opts=pulumi.ResourceOptions(parent=self)
        )

        # Deploy Bazarr
        bazarr = Bazarr(
            namespace=arr_stack_ns,
            opts=pulumi.ResourceOptions(parent=self)
        )

        # Store references
        self.namespace = arr_stack_ns
        # self.jellyfin = jellyfin  # Moved to dedicated GPU machine
        self.prowlarr = prowlarr
        self.flaresolverr = flaresolverr
        self.jellyseerr = jellyseerr
        self.sonarr = sonarr
        self.qbittorrent = qbittorrent
        self.bazarr = bazarr

        # Export useful information
        # self.jellyfin_url = jellyfin.web_url  # Moved to dedicated GPU machine
        self.prowlarr_url = prowlarr.web_url
        self.flaresolverr_url = flaresolverr.internal_url
        self.jellyseerr_url = jellyseerr.web_url
        self.sonarr_url = sonarr.web_url
        self.qbittorrent_url = qbittorrent.web_url
        self.bazarr_url = bazarr.web_url
