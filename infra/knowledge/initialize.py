"""Initialize one shared project without replacing existing knowledge."""

import json
import os
from pathlib import Path


def initialize(state, seeds):
    state = Path(state)
    notes = state / "notes" / "shared"
    config_dir = state / "config"
    for directory in (notes, config_dir, state / "caddy"):
        directory.mkdir(parents=True, exist_ok=True)
    config_file = config_dir / "config.json"
    config = json.loads(config_file.read_text()) if config_file.exists() else {}
    # Managed settings: all tenants remain in one searchable local project.
    config.update({
        "projects": {"shared": {"path": str(notes), "mode": "local"}},
        "default_project": "shared",
        "project_root": str(state / "notes"),
        "semantic_embedding_provider": "fastembed",
        "semantic_embedding_threads": 2,
    })
    temporary = config_file.with_suffix(".tmp")
    temporary.write_text(json.dumps(config, indent=2) + "\n")
    temporary.chmod(0o600)
    temporary.replace(config_file)
    for source in Path(seeds).glob("*.md"):
        destination = notes / "getting-started" / source.name
        destination.parent.mkdir(parents=True, exist_ok=True)
        # A later deployment must never undo an agent's corrections.
        try:
            with destination.open("x") as target:
                target.write(source.read_text())
        except FileExistsError:
            pass


if __name__ == "__main__":
    os.umask(0o077)
    initialize("/state", "/seed")
