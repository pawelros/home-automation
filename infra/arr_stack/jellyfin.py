import pulumi
import pulumi_kubernetes as kubernetes
from pulumi_kubernetes.helm.v3 import Release, ReleaseArgs, RepositoryOptsArgs


class Jellyfin(pulumi.ComponentResource):
    def __init__(self, namespace: kubernetes.core.v1.Namespace, opts=None):
        super().__init__(
            "jellyfin",
            "jellyfin",
            None,
            opts=opts,
        )

        # Deploy Jellyfin using Helm chart
        self.release = Release(
            "jellyfin",
            ReleaseArgs(
                chart="jellyfin",
                version="2.0.0",  # Working version from utkuozdemir
                repository_opts=RepositoryOptsArgs(
                    repo="https://utkuozdemir.org/helm-charts"
                ),
                namespace=namespace.metadata.name,
                values={
                    # Override the release name to get predictable service names
                    "fullnameOverride": "jellyfin",
                    
                    # Service configuration
                    "service": {
                        "type": "LoadBalancer",
                        "port": 80,
                        "annotations": {
                            "metallb.universe.tf/allow-shared-ip": "jellyfin",
                            "metallb.universe.tf/loadBalancerIPs": "192.168.1.40"
                        }
                    },
                    
                    # Persistence for configuration, cache, and media
                    "persistence": {
                        "config": {
                            "enabled": True,
                            "storageClass": "longhorn",
                            "size": "10Gi",
                            "accessMode": "ReadWriteOnce"
                        },
                        "cache": {
                            "enabled": True,
                            "storageClass": "longhorn", 
                            "size": "20Gi",
                            "accessMode": "ReadWriteOnce"
                        },
                        "data": {
                            "enabled": True,
                            "existingClaim": "arr-media-shared-ssd",  # Use migrated SSD PVC
                            "storageClass": "longhorn-ssd",
                            "size": "110Gi"
                        }
                    },
                    
                    # Resource limits - Increased for better transcoding performance
                    "resources": {
                        "limits": {
                            "cpu": "4000m",  # Increased from 2000m for transcoding
                            "memory": "6Gi"  # Increased from 4Gi
                        },
                        "requests": {
                            "cpu": "1000m",  # Increased from 500m
                            "memory": "2Gi"  # Increased from 1Gi
                        }
                    },
                    
                    # Timezone
                    "timezone": "UTC",
                    
                    # Security context - allow container to run as root for s6-supervise and GPU access
                    "podSecurityContext": {
                        "runAsUser": 0,  # Run as root to fix s6-supervise permissions
                        "runAsGroup": 0,
                        "fsGroup": 1000,  # Keep fsGroup for volume permissions
                        "supplementalGroups": [44, 109]  # video (44) and render (109) groups for GPU access
                    },
                    "securityContext": {
                        "allowPrivilegeEscalation": True,  # Required when privileged is True
                        "readOnlyRootFilesystem": False,
                        "runAsNonRoot": False,  # Allow root for s6-supervise
                        "privileged": True  # Required for GPU access
                    },
                    
                    # Environment variables
                    "env": {
                        "JELLYFIN_PublishedServerUrl": "http://192.168.1.40",
                        "PUID": "1000",
                        "PGID": "1000",
                        "JELLYFIN_FFMPEG_VAAPI_DEVICE": "/dev/dri/renderD128",
                        "JELLYFIN_FFMPEG_HWACCEL": "vaapi"
                    },
                    
                    # GPU device access for hardware acceleration
                    "extraVolumes": [
                        {
                            "name": "dri-devices",
                            "hostPath": {
                                "path": "/dev/dri",
                                "type": "Directory"
                            }
                        }
                    ],
                    "extraVolumeMounts": [
                        {
                            "name": "dri-devices",
                            "mountPath": "/dev/dri"
                        }
                    ],
                    
                    # Node affinity to ensure pod runs on k8s-node-1 where SSD is located
                    "nodeSelector": {
                        "kubernetes.io/hostname": "k8s-node-1"
                    },
                    
                    # Ingress configuration (disabled by default, using LoadBalancer)
                    "ingress": {
                        "enabled": False
                    }
                },
                timeout=180,
            ),
            opts=pulumi.ResourceOptions(parent=self),
        )

        # Store references
        self.namespace = namespace
        
        # Export useful information
        self.service_ip = pulumi.Output.concat("192.168.1.40")
        self.web_url = pulumi.Output.concat("http://192.168.1.40")
