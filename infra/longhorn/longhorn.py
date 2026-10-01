import json

import pulumi
import pulumi_kubernetes as kubernetes

# Backups go to the NAS rather than to the in-cluster object store. Its volume
# lives on Longhorn, so using it as the backup target would be circular: a
# Longhorn or disk failure would take the backups with it, and backing up
# object storage into itself grows without bound. The NAS is off-cluster,
# but its VM shares the Proxmox host with both workers; offsite backups are
# still needed to protect against a host or site failure.
BACKUP_TARGET = "nfs://192.168.1.127:/mnt/SSD/arr_stack/longhorn-backups"


class Longhorn(pulumi.ComponentResource):
    def __init__(self, opts=None):
        ns = kubernetes.core.v1.Namespace(
            "longhorn",
            metadata=kubernetes.meta.v1.ObjectMetaArgs(
                name="longhorn",
                labels={
                    "pod-security.kubernetes.io/enforce": "privileged",
                    "pod-security.kubernetes.io/audit": "privileged",
                    "pod-security.kubernetes.io/warn": "privileged",
                },
            ),
        )
        super().__init__(
            "longhorn",
            "longhorn",
            None,
            opts=pulumi.ResourceOptions(parent=ns),
        )

        longhorn = kubernetes.helm.v3.Release(
            "longhorn",
            name="longhorn",
            chart="longhorn",
            version="1.10.0",
            namespace=ns.metadata.name,
            repository_opts={
                "repo": "https://charts.longhorn.io",
            },
            values={
                "defaultSettings": {
                    "defaultDataPath": "/var/lib/longhorn",
                    # Most volumes here belong to workloads that are not always
                    # running. Without this, the recurring jobs below silently
                    # skip every detached volume and back up almost nothing.
                    "allowRecurringJobWhileVolumeDetached": True,
                    # Longhorn shares the nodes' root filesystem, so the stock
                    # 25% floor leaves too little schedulable room once the
                    # critical volumes carry a second replica. 18% still keeps a
                    # real margin (~26Gi on node-1, ~22Gi on node-2).
                    # The chart requires this one as a string.
                    "storageMinimalAvailablePercentage": "18",
                },
                "defaultBackupStore": {
                    # NFS needs no credential secret.
                    "backupTarget": BACKUP_TARGET,
                    "pollInterval": 300,
                },
                "persistence": {
                    "defaultClassReplicaCount": 1,
                    # Deleting a PVC now releases its PV instead of destroying the
                    # underlying Longhorn volume, so the data survives the mistake.
                    "reclaimPolicy": "Retain",
                },
            },
            opts=pulumi.ResourceOptions(parent=self, depends_on=[ns]),
        )

        # Recurring snapshot and backup jobs. Both target the "default" group,
        # which Longhorn applies to every volume that carries no explicit
        # recurring-job labels of its own. Monitoring uses a separate storage
        # class and cleanup group so snapshots and backups do not retain data
        # beyond the application's retention period.
        def recurring_job(name, cron, task, retain, concurrency):
            return kubernetes.apiextensions.CustomResource(
                name,
                api_version="longhorn.io/v1beta2",
                kind="RecurringJob",
                metadata=kubernetes.meta.v1.ObjectMetaArgs(
                    name=name,
                    namespace=ns.metadata.name,
                ),
                spec={
                    "name": name,
                    "cron": cron,
                    "task": task,
                    "groups": ["default"],
                    "retain": retain,
                    "concurrency": concurrency,
                },
                opts=pulumi.ResourceOptions(parent=self, depends_on=[longhorn]),
            )

        self.daily_snapshot = recurring_job(
            "daily-snapshot", "0 2 * * *", "snapshot", retain=7, concurrency=2
        )
        self.daily_backup = recurring_job(
            "daily-backup", "0 3 * * *", "backup", retain=14, concurrency=1
        )

        self.monitoring_cleanup = kubernetes.apiextensions.CustomResource(
            "monitoring-snapshot-cleanup",
            api_version="longhorn.io/v1beta2",
            kind="RecurringJob",
            metadata={"name": "monitoring-snapshot-cleanup", "namespace": ns.metadata.name},
            spec={
                "name": "monitoring-snapshot-cleanup",
                "cron": "0 4 * * *",
                "task": "snapshot-cleanup",
                "groups": ["monitoring"],
                "retain": 0,
                "concurrency": 1,
            },
            opts=pulumi.ResourceOptions(parent=self, depends_on=[longhorn]),
        )
        self.monitoring_trim = kubernetes.apiextensions.CustomResource(
            "monitoring-filesystem-trim",
            api_version="longhorn.io/v1beta2",
            kind="RecurringJob",
            metadata={"name": "monitoring-filesystem-trim", "namespace": ns.metadata.name},
            spec={
                "name": "monitoring-filesystem-trim",
                "cron": "0 5 * * *",
                "task": "filesystem-trim",
                "groups": ["monitoring"],
                "retain": 0,
                "concurrency": 1,
            },
            opts=pulumi.ResourceOptions(parent=self, depends_on=[longhorn]),
        )
        self.monitoring_storage_class = kubernetes.storage.v1.StorageClass(
            "longhorn-monitoring",
            metadata={"name": "longhorn-monitoring"},
            provisioner="driver.longhorn.io",
            allow_volume_expansion=True,
            reclaim_policy="Retain",
            volume_binding_mode="Immediate",
            parameters={
                "numberOfReplicas": "1",
                "staleReplicaTimeout": "30",
                "fsType": "ext4",
                "unmapMarkSnapChainRemoved": "enabled",
                "recurringJobSelector": json.dumps([{"name": "monitoring", "isGroup": True}]),
            },
            opts=pulumi.ResourceOptions(
                parent=self, depends_on=[self.monitoring_cleanup, self.monitoring_trim]
            ),
        )

        _ = kubernetes.core.v1.Service(
            "longhorn-ui",
            opts=pulumi.ResourceOptions(parent=self),
            metadata=kubernetes.meta.v1.ObjectMetaArgs(
                name="longhorn-ui",
                namespace="longhorn",
            ),
            spec=kubernetes.core.v1.ServiceSpecArgs(
                ports=[
                    kubernetes.core.v1.ServicePortArgs(
                        name="http",
                        port=80,
                        protocol="TCP",
                        target_port=8000,
                    ),
                ],
                selector={
                    "app": "longhorn-ui",
                },
                type="LoadBalancer",
                external_traffic_policy="Local",
            ),
        )
