# Copyright 2024 Matheus Vilano
# SPDX-License-Identifier: Apache-2.0

from grp import getgrnam
from os import getuid, getgid, chmod, chown, walk, path
from pathlib import Path
from stat import S_IXUSR, S_IXGRP, S_IXOTH

from helpers.config import SHARED_GROUP, EXTENSIONS_WHITELIST, BINARIES_WHITELIST, MIME_FILE, INSTALL_ROOT


def get_group_gid() -> int:
    """
    Resolve SHARED_GROUP to a gid, falling back to 'users' then 0.
    :return: The resolved group ID.
    """
    for candidate in (SHARED_GROUP, "users"):
        try:
            return getgrnam(candidate).gr_gid
        except KeyError:
            continue
    return 0


def get_current_user_uid() -> int:
    """
    Return uid of the user running this script.
    :return: The current user's ID.
    """
    return getuid()


def get_current_user_gid() -> int:
    """
    Return the primary gid of the user running this script.
    :return: The current user's primary group ID.
    """
    return getgid()


def set_permissions_recursive(target_dir: str | Path, gid: int, uid: int | None = None, dir_mode: int = 0o775,
                              file_mode: int = 0o664, exec_mode: int = 0o775) -> int:
    """
    Walk *target_dir* and set ownership + permissions for shared access.
    :param target_dir: The directory to process.
    :param gid: The group ID to set.
    :param uid: The user ID to set.
    :param dir_mode: The mode for directories.
    :param file_mode: The mode for regular files.
    :param exec_mode: The mode for executables.
    :return: The number of items processed.
    """
    processed = 0

    for root, dirs, files in walk(target_dir):

        try:  # Directory
            chmod(root, dir_mode)
            if uid is not None:
                chown(root, uid, gid)
        except (PermissionError, OSError):
            pass

        processed += 1

        for file in files:  # Files
            fpath = path.join(root, file)
            ext = path.splitext(file)[1]
            is_exec = ext in EXTENSIONS_WHITELIST or file in BINARIES_WHITELIST

            try:
                mode = exec_mode if is_exec else file_mode
                chmod(fpath, mode)
                if uid is not None:
                    chown(fpath, uid, gid)
            except (PermissionError, OSError):
                pass

            processed += 1

    return processed


def set_executable_bits(version_path_root: str | Path):
    """
    Ensure shell scripts and known binaries have +x.
    :param version_path_root: The root directory to scan.
    """
    version_path_root = Path(version_path_root)
    for version_path in version_path_root.rglob("*"):
        try:
            if version_path.suffix in EXTENSIONS_WHITELIST or version_path.name in BINARIES_WHITELIST:
                current = version_path.stat().st_mode
                version_path.chmod(current | S_IXUSR | S_IXGRP | S_IXOTH)
        except (PermissionError, OSError):
            pass


def create_mime_xml_file():
    """
    Copy the mime.xml file to the appropriate location.
    """
    mime_dir = Path("/usr/share/mime/packages")
    mime_dir.mkdir(parents=True, exist_ok=True)
    MIME_FILE.copy(mime_dir / MIME_FILE.name)


def remove_mime_xml_file():
    """
    Copy the mime.xml file to the appropriate location.
    """
    mime_path = Path(f"/usr/share/mime/packages/{MIME_FILE.name}")
    if not mime_path.is_file():
        return
    mime_path.unlink(missing_ok=True)


def create_desktop_file(version_name: str):
    """
    Generates a .desktop file to be used as shortcuts.
    :param version_name: The version name (e.g. "5.8.0") to use in the file name.
    """
    desktop_file = \
        f"""
    [Desktop Entry]
    Categories=AudioVideo;Development;Graphics;
    Comment=Advanced real-time 3D creation tool.
    Exec={INSTALL_ROOT}/{version_name}/Engine/Binaries/Linux/UnrealEditor %F
    Icon=unreal-engine
    MimeType=application/x-uproject
    Name=Unreal Engine {version_name}
    NoDisplay=false
    Path={INSTALL_ROOT}/{version_name}/Engine/Binaries/Linux
    PrefersNonDefaultGPU=false
    StartupNotify=true
    Terminal=false
    TerminalOptions=
    Type=Application
    X-KDE-SubstituteUID=false
    X-KDE-Username=
    """
    apps_dir = Path.home() / ".local" / "share" / "applications"
    apps_dir.mkdir(parents=True, exist_ok=True)
    (apps_dir / f"unreal-engine-{version_name.replace(".", "-")}.desktop").write_text(desktop_file)


def remove_desktop_file(version_name: str):
    """
    Deletes the .desktop file used as shortcuts.
    :param version_name: The version name (e.g. "5.8.0") to use when looking up the file path.
    """
    apps_dir = Path.home() / ".local" / "share" / "applications"
    desktop_path = apps_dir / f"unreal-engine-{version_name.replace(".", "-")}.desktop"
    if not desktop_path.is_file():
        return
    desktop_path.unlink(missing_ok=True)
