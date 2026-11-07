# Shared platform knowledge

This repository's knowledge scope is defined in `.knowledge.json`.
For infrastructure investigations, incident resolution, and architecture work,
use the platform-memory workflow in
`tools/codex/skills/platform-memory/SKILL.md`: retrieve relevant prior knowledge
before investigating and record verified findings afterward when the `knowledge`
MCP server is available. All tenants use its `shared` project; tenant/project
metadata identifies ownership and applicability.

If the service is unavailable, continue using available evidence and report the
limitation. Do not store secrets or claim that a note was saved without a
successful server response.
