# Copyright 2026 Matheus Vilano
# SPDX-License-Identifier: Apache-2.0

from os import access, X_OK
from pathlib import Path
from subprocess import Popen, DEVNULL


def find_editor_binary(version_path: str | Path):
    """
    Locate the UnrealEditor binary inside an extracted engine.
    :param version_path: Path to the engine installation.
    :return: The path to the binary as a string, or None if not found.
    """
    version_path = Path(version_path)

    # Commonly known locations (UE 5.x)
    candidates = [version_path / "Engine" / "Binaries" / "Linux" / "UnrealEditor",
                  version_path / "Engine" / "Binaries" / "Linux" / "UnrealEditor-Linux-Shipping", ]

    for c in candidates:
        if c.exists() and access(c, X_OK):
            return str(c)

    # Fall back: search for any file whose name starts with "UnrealEditor"
    for p in version_path.rglob("*"):
        if p.name.startswith("UnrealEditor") and p.is_file():
            return str(p)

    return None


def launch_editor(version_path: str | Path):
    """
    Spawn the editor in a detached process and return immediately.
    :param version_path: Path to the engine installation.
    """
    binary = find_editor_binary(version_path)
    if binary is None:
        raise FileNotFoundError(f"Could not locate the UnrealEditor binary inside {version_path}.")

    # Detach so the editor survives even if this manager closes
    Popen([binary], stdout=DEVNULL, stderr=DEVNULL, stdin=DEVNULL, start_new_session=True)
