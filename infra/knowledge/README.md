# Shared AI knowledge on deskmini

One Basic Memory project (`shared`) contains all tenants. Structured YAML
frontmatter identifies ownership and applicability; topic tags support discovery.
Notes remain Markdown on persistent storage, available to every device through
the same authenticated MCP endpoint. Scope metadata is not access control.

The deskmini deployment is available at `https://192.168.1.29/mcp` and
`https://knowledge.lab/mcp`. The IP endpoint works without Pi-hole DNS. Both
require the local CA certificate and bearer authentication. Runtime notes,
indexes, and embeddings stay on deskmini. Pulumi Cloud holds deployment state,
including starter-note ConfigMaps and encrypted deployment credentials; it is
not a synchronization destination for notes created through MCP.

## Components

- Basic Memory `0.24.1`, bound to pod loopback, with SQLite and local FastEmbed
  embeddings. Initial startup downloads its embedding model; allow outbound HTTPS.
- Caddy `2.10.2`, providing HTTPS and bearer authentication. No access log is
  configured. Its administration endpoint is disabled.
- One 10 GiB Longhorn volume stores notes, configuration, index, embedding cache,
  and the private certificate authority. The PVC is Pulumi-protected. Existing
  Longhorn default-group snapshots/backups cover it; inspect backup success after
  deployment. Those backups share the Proxmox failure domain, so keep an offsite
  copy too.
- A single replica with `Recreate` updates avoids concurrent SQLite writers and
  volume-attachment conflicts. Expect brief downtime during updates.
- A MetalLB-assigned address and ExternalDNS name `knowledge.lab`. Connect from
  your LAN, or through an existing VPN that routes the LAN and its DNS.
  This change does not create public access or a VPN.

Basic Memory's HTTP transport has no authentication. Do not expose its port 8000.
Only the sidecar reaches it. The Service exposes the TLS gateway on port 443.
All clients holding the token can read and write all tenants.

## Enable and deploy

Run from `infra/` with the deskmini stack and Kubernetes context available.
The feature is opt-in; existing stacks remain unchanged until enabled.

```sh
python3 -c 'import secrets; print(secrets.token_urlsafe(48))' | pulumi config set knowledge:token --secret --stack deskmini
pulumi config set knowledge:hostname knowledge.lab --stack deskmini
pulumi config set knowledge:address 192.168.1.29 --stack deskmini
pulumi config set knowledge:enabled true --stack deskmini
pulumi preview --stack deskmini --diff
pulumi up --stack deskmini
kubectl --context deskmini -n knowledge rollout status deployment/knowledge --timeout=900s
kubectl --context deskmini -n knowledge get service knowledge
```

The token passes directly into Pulumi's encrypted config. Never paste it into
source, chat, or shell arguments. A token change triggers pod recreation.
Review the full preview for unrelated changes before applying. Use a targeted
update if the existing stack has unrelated drift.

The initializer creates the shared project and starter notes only when absent;
redeployment does not overwrite edited knowledge. Starter architecture is based
on repository configuration and explicitly marked as not verified live.

## Connect each device

First make `knowledge.lab` resolve to the Service address through Pi-hole or
your VPN DNS, or use the IP endpoint. An arbitrary internet-connected device
cannot reach this private service without a LAN/VPN route.

Export the public root certificate through authenticated cluster access:

```sh
kubectl --context deskmini -n knowledge exec deployment/knowledge -c gateway -- cat /state/caddy/data/caddy/pki/authorities/local/root.crt > /tmp/knowledge-root.crt
openssl x509 -in /tmp/knowledge-root.crt -noout -fingerprint -sha256
```

Transfer this public certificate to each device through a trusted channel and
verify the fingerprint. Import it as a trusted root in that device's certificate
store. Do not copy the CA private key or disable certificate verification.
On macOS, use Keychain Access to import the certificate and explicitly trust it
for SSL. Other clients may require their own CA-bundle configuration.

Make the bearer token available as `KNOWLEDGE_TOKEN` in the environment of the
Codex process, preferably injected from your password manager. Retrieve it via
Pulumi's secret configuration directly into that secure destination, without
printing it. Interactive CLI users can use a hidden prompt:

```sh
read -rs 'KNOWLEDGE_TOKEN?Knowledge token: '
export KNOWLEDGE_TOKEN
```

The example above uses zsh. Desktop applications launched from Finder do not
inherit a terminal's environment; configure their launch environment or launch
Codex from the configured terminal. Do not put the token in `AGENTS.md` or a
checked-in TOML file.

Register the endpoint on each device:

```sh
codex mcp add knowledge --url https://knowledge.lab/mcp --bearer-token-env-var KNOWLEDGE_TOKEN
codex mcp list
```

For background Codex clients that cannot inherit `KNOWLEDGE_TOKEN`, the bundled
`tools/codex/knowledge_headers.py` can supply authentication through Codex's
`http_headers_helper` setting. Copy it into
`~/.config/deskmini-knowledge/knowledge_headers.py` and store the token in
`~/.config/deskmini-knowledge/token`, owned by your user with mode `600` and a
parent directory with mode `700`. Keep this directory outside repository and
cloud-synchronized folders. The helper prefers `KNOWLEDGE_TOKEN` when present;
otherwise it reads that private file. Its stdout contains credentials for Codex
to consume; do not run it directly in a terminal or paste its output.

For example, use the following instead of the bearer-environment registration
above, substituting your actual absolute executable and helper paths:

```toml
[mcp_servers.knowledge]
url = "https://192.168.1.29/mcp"
http_headers_helper = "/absolute/path/to/python3 /absolute/path/to/knowledge_headers.py"
startup_timeout_sec = 30
tool_timeout_sec = 60
```

The laptop used for deployment already has this configuration and a local token
file. Its public CA is at `~/.config/deskmini-knowledge/root.crt`. Clients need
to trust that CA through their certificate store or an explicit CA setting. For
Codex CLI, an explicit CA can be supplied without disabling TLS verification:

```sh
CODEX_CA_CERTIFICATE="$HOME/.config/deskmini-knowledge/root.crt" codex
```

For background apps, set that variable in the Codex host's launch environment
and restart the host, or complete OS certificate-store trust. Starting a new
chat alone does not change the environment of an existing host process. Other
devices need their own CA, credential configuration, and installed skill; they
share the same server.

Install `tools/codex/skills/platform-memory` from this repository into that
device's `~/.codex/skills/platform-memory`, then start a new Codex session.
This repository's `AGENTS.md` also references the workflow directly.
For other repositories, add a `.knowledge.json` like the root example, changing
the tenant, projects, and environments. Reference the platform-memory workflow
from their repository instructions to make recall/capture an explicit convention.

Self-hosting storage does not make Codex inference local. Retrieved note content
becomes model context. Follow the relevant employer's rules for storing and
processing work data.

## Deployment notes

The official Caddy binary carries the `NET_BIND_SERVICE` file capability.
The gateway needs it in its capability bounding set even though it listens on
8443; dropping it prevents execution with `operation not permitted`. The pod
still runs as a non-root user and drops other capabilities.

The commissioning note was written from the laptop, retrieved from the controller,
and retrieved again after a pod restart. Tenant filtering and local embedding
index readiness were checked. Backup jobs are configured, but a successful
backup/restore of this new volume has not yet been verified.

## Metadata and filtering

The starter `getting-started/knowledge-conventions` note defines the schema.
Use `tenant` for ownership, arrays `projects` and `environments` for applicability,
`type` for note kind, and `tags` for topics. Record source evidence and freshness.
Example search arguments:

```json
{
  "project": "shared",
  "query": "runner memory scheduling",
  "search_type": "hybrid",
  "metadata_filters": {
    "tenant": {"$in": ["personal", "general"]},
    "projects": {"$contains": "github-runners"}
  },
  "page_size": 5
}
```

Omit the project filter when investigating platform-wide dependencies. Remove
the tenant filter when deliberately searching for approaches from other work;
keep their original attribution. Metadata filters also work without a text query.
Use `search_type: "text"` when semantic indexing is unavailable.

## Acceptance and operations

After rollout, check that a request without a bearer token returns 401, a valid
client can initialize MCP and list tools, and the two starter notes are searchable.
Create an attributed disposable note on device A and retrieve it from device B.
Confirm tenant/project filters before adding substantive knowledge. Preserve
source attribution when capturing incidents; never import raw credentials/logs.

For restore, stop the Deployment, restore the whole Longhorn volume from a
consistent backup, then restart. Restoring only Markdown can rebuild the index
but loses the CA and other state; replacing the CA requires redistributing trust.
Deleting the PVC requires deliberately removing Pulumi protection. Do not disable
the feature after deployment without reviewing the resulting deletion plan.

## Sources

- https://docs.basicmemory.com/reference/docker
- https://docs.basicmemory.com/reference/mcp-tools-reference
- https://docs.basicmemory.com/concepts/knowledge-format
- https://learn.chatgpt.com/docs/extend/mcp
