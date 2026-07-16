# Copyright 2026 Matheus Vilano
# SPDX-License-Identifier: Apache-2.0

from pathlib import Path

APP_ICON = Path(__file__).parent.parent / "resources" / "icon.gif"
"""Path to the application icon."""

MIME_FILE = Path(__file__).parent.parent / "resources" / "mime.xml"
"""Path to the MIME XML file."""

INSTALL_ROOT = Path("/opt/unreal-engine-bin")
"""Root directory for all installed engine versions."""

SHARED_GROUP = "users"
"""Group that all target users belong to."""

REQUIRED_FOLDERS = {"Engine", "FeaturePacks", "Templates"}
"""Folders that must exist for a valid UE installation."""

EXTENSIONS_WHITELIST = {".sh", ".py", ""}
"""Extension whitelist for setting executable bits."""

BINARIES_WHITELIST = {"UnrealEditor",
                      "UnrealEditor-Linux-Shipping",
                      "CrashReportClient",
                      "ShaderCompileWorker",
                      "ld.lld"}
"""Binaries whitelist for setting executable bits."""
