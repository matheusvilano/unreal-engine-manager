#!/usr/bin/env python3

from pathlib import Path

from source.config import REQUIRED_FOLDERS


def validate_extraction(target_path: str | Path):
    """
    Verify the extracted archive contains the required UE folders.
    :param target_path: The path to the extracted directory.
    :raises ValueError: If required folders are missing.
    """
    missing = []
    for folder in REQUIRED_FOLDERS:
        if not (Path(target_path) / folder).exists():
            missing.append(folder)

    if missing:
        raise ValueError(f"Validation failed: the following required folders are "
                         f"missing: {', '.join(missing)}.\n"
                         f"This does not appear to be a valid Unreal Engine archive.")
