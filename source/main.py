#!/usr/bin/env python3

"""
Unreal Engine Manager - Multi-user shared installation manager for Linux.
Uses only Python standard library (tkinter, zipfile, os, etc.).

Flow:
  - List installed UE versions detected in /opt/unreal-engine/<version>/
  - Launch editor for a selected version
  - Install a new version from a user-supplied ZIP archive
  - Automatic permission setup for shared multi-user access
"""

from app import UnrealManagerApp


def main():
    """Entry point for the application."""
    app = UnrealManagerApp()
    app.mainloop()


if __name__ == "__main__":
    main()
