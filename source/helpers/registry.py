# Copyright 2026 Matheus Vilano
# SPDX-License-Identifier: Apache-2.0

from dataclasses import dataclass
from pathlib import Path

from helpers.config import INSTALL_ROOT, REQUIRED_FOLDERS


@dataclass
class UnrealInstallation:

    version: str
    """Version number (e.g. 5.8.0)."""

    path: Path
    """Path pointing to the root directory of the installation"""

    interrupted: bool = False
    """Whether this is an interrupted and incomplete installation."""

def load() -> tuple[UnrealInstallation, ...]:
    """
    Loads the registry by scanning the installation root.
    :return: Discovered Unreal Engine installations.
    """
    installations = []

    if INSTALL_ROOT.exists():
        for child in INSTALL_ROOT.iterdir():
            if not child.is_dir():
                continue
            if child.name.startswith(".") or child.name == "__pycache__":
                continue
            interrupted = (child / ".installing").exists()
            if interrupted or all((child / folder).exists() for folder in REQUIRED_FOLDERS):
                installations.append(UnrealInstallation(child.name, child, interrupted))

    return tuple(installations)
