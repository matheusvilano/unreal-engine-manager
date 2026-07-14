# Copyright 2024 Matheus Vilano
# SPDX-License-Identifier: Apache-2.0

from pathlib import Path

from helpers.config import INSTALL_ROOT, REQUIRED_FOLDERS


def load() -> dict[str, Path]:
    """
    Loads the registry by scanning the installation root.
    :return: A dictionary of version names and their paths.
    """
    versions = {}

    if INSTALL_ROOT.exists():
        for child in INSTALL_ROOT.iterdir():
            if not child.is_dir():
                continue
            if child.name.startswith(".") or child.name == "__pycache__":
                continue
            if all((child / folder).exists() for folder in REQUIRED_FOLDERS):
                versions[child.name] = str(child)

    return versions
