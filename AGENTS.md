# Unreal Engine Manager – Agent Quick‑Start

## How to launch the application
- `python ./source/main.py` – runs the GUI.
  - The script has a shebang, so it can also be executed directly after making it executable: `chmod +x source/main.py && ./source/main.py`.

## Runtime prerequisites
- Python 3 (any recent version).
- Tkinter (`tk`) – install via your package manager (e.g., `sudo pacman -S tk`).
- No additional pip packages are required; the code uses only the standard library.

## Typical usage patterns
- **Refresh** installed UE versions: click *[↻] Refresh* or press `R`/`r`.
- **Open download page**: click *[↓] Get* or press `G`/`g`.
- **Install a new version**: click *[+] Add* or press `A`/`a`, then choose a ZIP file from the dialog.
- **Uninstall**: select a version and click *[–] Delete* or press `D`/`d`.
- **Launch editor**: select a version, enable the button, then click *Launch Editor* or press `L`/`l`/`Return`.

## Keyboard shortcuts (for power users)
```
R/r – Refresh list
G/g – Open UE download page
A/a – Add new installation from ZIP
D/d – Delete selected version
L/l/Enter – Launch editor for selected version
Arrow keys – Navigate the grid of versions
```

## Development notes
- The project is a single‑file GUI; no build or test scripts are provided.
- Source layout: `source/main.py` contains the entry point, while helper modules live in `source/helpers/`.
- No CI configuration is present – contributors should run the app locally to verify changes.

---
*This file is intended for OpenCode agents to quickly understand how to run and interact with Unreal Engine Manager.*