"""Codex HTTP header helper; its stdout is consumed directly by Codex."""

import json
import os
from pathlib import Path
import stat
import sys


def read_headers(path=None):
    token = os.environ.get("KNOWLEDGE_TOKEN")
    if not token:
        path = Path(path) if path else Path.home() / ".config/deskmini-knowledge/token"
        mode = path.stat()
        if mode.st_mode & (stat.S_IRWXG | stat.S_IRWXO) or mode.st_uid != os.getuid():
            raise ValueError("Knowledge token file must belong to this user and have mode 600")
        token = path.read_text().strip()
    if not token or any(character.isspace() for character in token):
        raise ValueError("Knowledge token must be a non-empty value without whitespace")
    return {"Authorization": "Bearer " + token}


if __name__ == "__main__":
    try:
        print(json.dumps(read_headers()))
    except (OSError, ValueError) as error:
        print("Knowledge authentication unavailable: " + str(error), file=sys.stderr)
        raise SystemExit(1)
