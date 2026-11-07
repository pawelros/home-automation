---
title: Home platform entry point
type: architecture
tenant: personal
projects: [home-automation]
environments: [deskmini]
tags: [kubernetes, pulumi, platform]
status: documented
recorded_at: '2026-11-06'
verified_at: null
sources:
  - home-automation/infra/__main__.py
  - home-automation/infra/longhorn/longhorn.py
  - home-automation/infra/rustfs/rustfs.py
---

# Home platform entry point

This note describes repository configuration, not a verified live inventory.
Read the current source and inspect the live cluster before operational changes.

## Observations

- [architecture] `infra/` defines the deskmini Kubernetes platform in Python/Pulumi.
- [storage] Longhorn provides persistent storage; application volumes use the
  default backup group. Daily backups target a NAS outside Kubernetes.
- [constraint] The NAS shares the Proxmox host with workers. These backups do
  not protect against losing the entire host or site.
- [observability] Alloy collects telemetry, Loki stores logs, Mimir stores
  metrics, and Grafana provides access. Loki and Mimir use RustFS object storage.
- [networking] MetalLB exposes LoadBalancer services. ExternalDNS publishes
  `.lab` names to Pi-hole; mDNS publication supports local discovery.
- [database] CloudNativePG manages PostgreSQL, including Home Assistant storage.
- [scope] Home automation is personal knowledge, separate in attribution from
  employer platforms even though both are searchable in this shared store.

## Where to start

Read `infra/__main__.py` for component wiring and the relevant module for details.
Use the `deskmini` Kubernetes context explicitly. Repository configuration may
have changed since this note was created; `verified_at` remains unset until a
live check is completed.
