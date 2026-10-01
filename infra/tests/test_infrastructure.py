import json
import runpy
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace

import pulumi
from pulumi.runtime import Mocks, set_mocks, test
from pulumi.runtime.config import set_all_config


INFRA = Path(__file__).resolve().parents[1]


class InfrastructureMocks(Mocks):
    def __init__(self):
        self.resources = []

    def new_resource(self, args):
        # Pulumi wraps any collection containing a secret. Decode test-only
        # values for assertions while preserving wrappers in resource outputs.
        def decode(value):
            if isinstance(value, dict):
                if "4dabf18193072939515e22adb298388d" in value:
                    return decode(value["value"])
                return {key: decode(item) for key, item in value.items()}
            if isinstance(value, list):
                return [decode(item) for item in value]
            return value

        self.resources.append(SimpleNamespace(typ=args.typ, name=args.name, inputs=decode(args.inputs)))
        return [args.name, args.inputs]

    def call(self, args):
        return args.args


class InfrastructureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mocks = InfrastructureMocks()
        set_mocks(cls.mocks, project="home-automation", stack="test", preview=False)
        set_all_config({
            "home-automation:home-assistant-token": "test-only",
            "home-automation:influxdb-admin-password": "test-only",
            "home-automation:influxdb-admin-token": "test-only",
            "home-automation:object-storage-secret-key": "test-only",
        })
        sys.path.insert(0, str(INFRA))

        @test
        def load_program():
            runpy.run_path(str(INFRA / "__main__.py"))

        load_program()

    def resource(self, resource_type, name):
        return next(
            resource
            for resource in self.mocks.resources
            if resource.typ == resource_type and resource.name == name
        )

    def test_retired_services_are_not_deployed(self):
        names = {resource.name for resource in self.mocks.resources}
        self.assertTrue(names.isdisjoint({"unifi-controller", "unify", "tailscale-namespace", "home-subnet-router"}))

        config = self.resource("kubernetes:core/v1:ConfigMap", "homepage")
        services = config.inputs["data"]["services.yaml"].lower()
        self.assertNotIn("unifi", services)
        self.assertNotIn("tailscale", services)
        self.assertNotIn("${", services)

    def test_qbittorrent_can_schedule_on_either_worker(self):
        release = self.resource("kubernetes:helm.sh/v3:Release", "qbittorrent")
        values = release.inputs["values"]
        self.assertFalse(values.get("affinity"))
        self.assertTrue(release.inputs["resetValues"])
        self.assertNotIn("nodeSelector", values)
        self.assertEqual(values["persistence"]["downloads"]["existingClaim"], "arr-shared-nfs")

    def test_backups_cover_detached_volumes_and_preserve_released_data(self):
        release = self.resource("kubernetes:helm.sh/v3:Release", "longhorn")
        values = release.inputs["values"]
        self.assertTrue(values["defaultSettings"]["allowRecurringJobWhileVolumeDetached"])
        self.assertEqual(values["persistence"]["reclaimPolicy"], "Retain")
        self.assertTrue(values["defaultBackupStore"]["backupTarget"].startswith("nfs://"))

        backup = self.resource("kubernetes:longhorn.io/v1beta2:RecurringJob", "daily-backup")
        self.assertEqual(backup.inputs["spec"]["task"], "backup")
        self.assertIn("default", backup.inputs["spec"]["groups"])

    def test_helm_updates_cannot_select_an_unpinned_chart(self):
        releases = [resource for resource in self.mocks.resources if resource.typ == "kubernetes:helm.sh/v3:Release"]
        self.assertGreater(len(releases), 0)
        for release in releases:
            with self.subTest(release=release.name):
                self.assertTrue(release.inputs.get("version"))

    def test_monitoring_volumes_do_not_receive_application_snapshots(self):
        storage = self.resource("kubernetes:storage.k8s.io/v1:StorageClass", "longhorn-monitoring")
        selectors = json.loads(storage.inputs["parameters"]["recurringJobSelector"])
        self.assertEqual(selectors, [{"name": "monitoring", "isGroup": True}])
        self.assertEqual(storage.inputs["parameters"]["unmapMarkSnapChainRemoved"], "enabled")
        for name, task in [("monitoring-snapshot-cleanup", "snapshot-cleanup"),
                           ("monitoring-filesystem-trim", "filesystem-trim")]:
            job = self.resource("kubernetes:longhorn.io/v1beta2:RecurringJob", name)
            self.assertEqual(job.inputs["spec"]["groups"], ["monitoring"])
            self.assertEqual(job.inputs["spec"]["task"], task)
        rustfs = self.resource("kubernetes:core/v1:PersistentVolumeClaim", "rustfs-data")
        self.assertEqual(rustfs.inputs["spec"]["storageClassName"], "longhorn-monitoring")
        loki = self.resource("kubernetes:helm.sh/v3:Release", "loki").inputs["values"]
        for role in ("backend", "write"):
            self.assertEqual(loki[role]["persistence"]["storageClass"], "longhorn-monitoring")
        mimir = self.resource("kubernetes:helm.sh/v3:Release", "mimir").inputs["values"]
        for role in ("compactor", "ingester", "store_gateway", "alertmanager"):
            self.assertEqual(mimir[role]["persistentVolume"]["storageClass"], "longhorn-monitoring")

    def test_log_and_metric_retention_are_enforced_by_compactors(self):
        loki = self.resource("kubernetes:helm.sh/v3:Release", "loki").inputs["values"]["loki"]
        self.assertEqual(loki["limits_config"]["retention_period"], "168h")
        self.assertTrue(loki["compactor"]["retention_enabled"])
        mimir = self.resource("kubernetes:helm.sh/v3:Release", "mimir").inputs["values"]
        self.assertEqual(mimir["mimir"]["structuredConfig"]["limits"]["compactor_blocks_retention_period"], "336h")

    def test_rustfs_and_consumers_share_credentials_and_buckets(self):
        from rustfs.rustfs import BUCKETS

        release = self.resource("kubernetes:helm.sh/v3:Release", "rustfs")
        self.assertTrue(release.inputs["values"]["mode"]["standalone"]["enabled"])
        self.assertFalse(release.inputs["values"]["mode"]["distributed"]["enabled"])
        self.assertEqual(release.inputs["values"]["secret"]["existingSecret"], "rustfs-credentials")
        names = {resource.name for resource in self.mocks.resources}
        self.assertNotIn("minio", names)
        secret = self.resource("kubernetes:core/v1:Secret", "rustfs-credentials").inputs["stringData"]
        loki = self.resource("kubernetes:helm.sh/v3:Release", "loki").inputs["values"]["loki"]
        mimir = self.resource("kubernetes:helm.sh/v3:Release", "mimir").inputs["values"]["mimir"]["structuredConfig"]
        self.assertEqual(loki["storage"]["s3"]["secretAccessKey"], secret["RUSTFS_SECRET_KEY"])
        self.assertEqual(mimir["common"]["storage"]["s3"]["secret_access_key"], secret["RUSTFS_SECRET_KEY"])
        buckets = set(loki["storage"]["bucketNames"].values())
        buckets.update(mimir[role]["s3"]["bucket_name"] for role in ("alertmanager_storage", "ruler_storage"))
        buckets.add(mimir["common"]["storage"]["s3"]["bucket_name"])
        self.assertEqual(buckets, set(BUCKETS))
        job = self.resource("kubernetes:batch/v1:Job", "rustfs-buckets")
        container = job.inputs["spec"]["template"]["spec"]["containers"][0]
        for bucket in buckets:
            self.assertIn(bucket, container["command"][2])
        credentials = {env["name"]: env for env in container["env"]}
        self.assertIn("valueFrom", credentials["AWS_SECRET_ACCESS_KEY"])


if __name__ == "__main__":
    unittest.main()
