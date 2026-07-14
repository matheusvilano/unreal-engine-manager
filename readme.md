# Unreal Engine Manager

## Summary

A Python-based Linux application for managing Unreal Engine installations. This is not a fancy Epic Games Launcher
replacement - instead, this application is meant to be minimal and bloat-free. Put simply, it is a GUI-enabled and
user-friendly alternative to the unreal-engine-bin AUR package.

## Installation

This package will soon be available on the [Arch User Repository](https://aur.archlinux.org/). When that happens, this
README will be updated to reflect the new installation instructions. In the meantime, you can use this application by
cloning this repository, setting its root as the current working directory, then running `python ./source/main.py`.

## Features

The Unreal Engine Manager is capable of performing the following tasks:

- Fetching Unreal Engine installations from `/opt/unreal-engine-bin/`.
- Opening the Unreal Engine for Linux downloads page.
- Installing a new Unreal Engine version from a user-sourced ZIP archive.
- Associating Unreal Engine project files (`.uproject`) with Unreal Engine.
- Generating a new `.desktop` shortcut for a specific Unreal Engine version.
- Launching the Unreal Editor for a specific Unreal Engine version.
- Uninstalling a specific version of Unreal Engine.
