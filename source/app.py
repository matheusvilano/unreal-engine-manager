# Copyright 2024 Matheus Vilano
# SPDX-License-Identifier: Apache-2.0

from getpass import getuser
from os import access, W_OK
from pathlib import Path
from shlex import quote
from shutil import rmtree as sh_rmtree, move as sh_move
from subprocess import run, CalledProcessError
from threading import Thread
from tkinter import Tk, Canvas, StringVar, Toplevel, PhotoImage
from tkinter.filedialog import askopenfilename as tk_filedialog_askopenfilename
from tkinter.messagebox import (showerror as tk_msgbox_showerror, askyesno as tk_msgbox_askyesno,
                                showinfo as tk_msgbox_showinfo)
from tkinter.ttk import Frame, Button, Label, Scrollbar, Radiobutton, Progressbar, Style
from webbrowser import open as web_open
from zipfile import ZipFile

from helpers import registry, unreal, gui, zip, system
from helpers.config import INSTALL_ROOT, REQUIRED_FOLDERS, SHARED_GROUP

# UI Constants

_COLOR_BG_DARK = "#1e1e1e"
_COLOR_BG_MID = "#2d2d2d"
_COLOR_BG_LIGHT = "#3d3d3d"
_COLOR_FG = "#efefef"
_COLOR_ACCENT = "#061224"
_FONT_VERSION_LABEL = ("TkDefaultFont", 16, "bold")


class UnrealManagerApp(Tk):
    """
    Unreal Engine Manager application user interface.
    """

    def __init__(self):
        """
        Constructor for the Unreal Manager application.
        """
        super().__init__()

        # Core
        self.title("Unreal Engine Manager")
        self.geometry("1000x500")
        self.minsize(1000, 500)
        self.configure(background=_COLOR_BG_DARK)
        self.resizable(False, False)

        # Icon
        icon_path = Path(__file__).resolve().parent.parent / "resources" / "icon.gif"
        icon = PhotoImage(file=str(icon_path))
        self.iconphoto(False, icon)

        # Styling
        self._style = Style()
        self._style.theme_use("clam")
        self._style.configure(".", background=_COLOR_BG_DARK, foreground=_COLOR_FG, fieldbackground=_COLOR_BG_DARK)
        self._style.configure("TFrame", background=_COLOR_BG_DARK)
        self._style.configure("TLabel", background=_COLOR_BG_DARK, foreground=_COLOR_FG)
        self._style.configure("TButton", background=_COLOR_BG_LIGHT, foreground=_COLOR_FG, borderwidth=1,
                              focuscolor=_COLOR_ACCENT, bordercolor=_COLOR_BG_DARK, lightcolor=_COLOR_BG_DARK,
                              darkcolor=_COLOR_BG_DARK)
        self._style.map("TButton", background=[("pressed", _COLOR_BG_DARK), ("active", _COLOR_BG_MID)],
                        foreground=[("disabled", "#7d7d7d")])
        self._style.configure("TRadiobutton", background=_COLOR_BG_MID, foreground=_COLOR_FG, font=_FONT_VERSION_LABEL,
                              anchor="center")
        self._style.configure("Toolbutton.TRadiobutton", background=_COLOR_BG_MID, foreground=_COLOR_FG,
                              font=_FONT_VERSION_LABEL, anchor="center", padding=10,
                              bordercolor=_COLOR_BG_DARK, lightcolor=_COLOR_BG_DARK, darkcolor=_COLOR_BG_DARK)
        self._style.map("TRadiobutton", background=[("active", _COLOR_BG_LIGHT)],
                        indicatorcolor=[("selected", _COLOR_ACCENT), ("!selected", _COLOR_BG_LIGHT)])
        self._style.map("Toolbutton.TRadiobutton",
                        background=[("pressed", _COLOR_BG_DARK), ("active", _COLOR_BG_DARK),
                                    ("selected", _COLOR_ACCENT)],
                        foreground=[("selected", _COLOR_FG)])
        self._style.configure("Vertical.TScrollbar", gripcount=0, background=_COLOR_BG_LIGHT,
                              troughcolor=_COLOR_BG_MID, bordercolor=_COLOR_BG_DARK,
                              lightcolor=_COLOR_BG_DARK, darkcolor=_COLOR_BG_DARK,
                              arrowcolor=_COLOR_FG)
        self._style.configure("List.TFrame", background=_COLOR_BG_MID)
        self._style.configure("List.TLabel", background=_COLOR_BG_MID, foreground=_COLOR_FG)
        self._style.configure("Horizontal.TProgressbar", background=_COLOR_ACCENT, troughcolor=_COLOR_BG_MID,
                              bordercolor=_COLOR_BG_DARK, lightcolor=_COLOR_ACCENT, darkcolor=_COLOR_ACCENT)

        self._versions = dict[str, Path]()  # {name: path}
        self._install_thread: Thread

        # Header
        header = Frame(self, padding=(12, 8))
        header.pack(fill="x")
        # Label(header, text="Installed Versions", font=("TkDefaultFont", 14, "bold")).pack(side="left")

        # Toolbar
        toolbar = Frame(header)
        toolbar.pack(side="top", fill="x")
        self._button_refresh = Button(toolbar, text="[↻] Refresh", underline=4, command=self._on_refresh_button_clicked)
        self._button_refresh.pack(side="left", padx=4, expand=True, fill="x")
        self._bind_status_info(self._button_refresh, "Refresh the list of installed versions.")
        self._button_get = Button(toolbar, text="[↓] Get", underline=4, command=self._on_get_button_clicked)
        self._button_get.pack(side="left", padx=4, expand=True, fill="x")
        self._bind_status_info(self._button_get, "Open the Unreal Engine for Linux web page.")
        self._button_add = Button(toolbar, text="[+] Add", underline=4, command=self._on_add_button_clicked)
        self._button_add.pack(side="left", padx=4, expand=True, fill="x")
        self._bind_status_info(self._button_add, "Install a new Unreal Engine version from a ZIP archive.")
        self._button_remove = Button(toolbar, text="[–] Delete", underline=4, command=self._on_remove_button_clicked)
        self._button_remove.pack(side="left", padx=4, expand=True, fill="x")
        self._bind_status_info(self._button_remove, "Uninstall the selected Unreal Engine version.")

        # Main content: scrollable list
        content = Frame(self, padding=12)
        content.pack(fill="both", expand=True)
        canvas = Canvas(content, highlightthickness=0, background=_COLOR_BG_MID)
        scrollbar = Scrollbar(content, orient="vertical", command=canvas.yview)
        self._scroll_frame = Frame(canvas, style="List.TFrame")
        self._scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        window_id = canvas.create_window((0, 0), window=self._scroll_frame, anchor="nw")

        def _on_canvas_configure(e):
            canvas.itemconfig(window_id, width=e.width)

        canvas.bind("<Configure>", _on_canvas_configure)
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Tooltips
        self._tooltip_var = StringVar(value="")
        status_bar = Frame(self, padding=(12, 4))
        status_bar.pack(fill="x", side="bottom")
        Label(status_bar, textvariable=self._tooltip_var).pack(side="left")
        self._button_launch = Button(status_bar, text="Launch Editor", underline=0,
                                     command=self._on_launch_button_clicked,
                                     state="disabled")
        self._button_launch.pack(side="right")
        self._bind_status_info(self._button_launch, "Launch the editor for the selected version and exit.")
        self._selected_version = StringVar()
        self._version_cards = {}  # radiobutton widgets keyed by version name
        self._setup_bindings()
        self.refresh()

    @property
    def versions(self) -> list[str]:
        """
        :return: A list of version names, sorted (newest/highest first).
        """
        return list(reversed(sorted(self._versions.keys())))

    def _setup_bindings(self):
        """
        Bind keyboard shortcuts to application actions.
        """
        self.bind("<r>", lambda _: self._on_refresh_button_clicked())
        self.bind("<R>", lambda _: self._on_refresh_button_clicked())
        self.bind("<g>", lambda _: self._on_get_button_clicked())
        self.bind("<G>", lambda _: self._on_get_button_clicked())
        self.bind("<a>", lambda _: self._on_add_button_clicked())
        self.bind("<A>", lambda _: self._on_add_button_clicked())
        self.bind("<d>", lambda _: self._on_remove_button_clicked())
        self.bind("<D>", lambda _: self._on_remove_button_clicked())
        self.bind("<l>", lambda _: self._on_launch_button_clicked())
        self.bind("<L>", lambda _: self._on_launch_button_clicked())
        self.bind("<Return>", lambda _: self._on_launch_button_clicked())
        self.bind("<Left>", lambda _: self._navigate_versions("left"))
        self.bind("<Right>", lambda _: self._navigate_versions("right"))
        self.bind("<Up>", lambda _: self._navigate_versions("up"))
        self.bind("<Down>", lambda _: self._navigate_versions("down"))

    def _navigate_versions(self, direction: str):
        """
        Navigate the version grid using arrow keys.
        :param direction: One of 'left', 'right', 'up', 'down'.
        """
        if not self._versions:
            return

        current = self._selected_version.get()

        if current not in self.versions:
            if self.versions:
                self._selected_version.set(self.versions[0])
                self._on_version_button_clicked()
            return

        index = self.versions.index(current)
        columns = 3
        row = index // columns
        col = index % columns
        rows = (len(self.versions) + columns - 1) // columns

        if direction == "left":
            if index > 0:
                index -= 1
        elif direction == "right":
            if index < len(self.versions) - 1:
                index += 1
        elif direction == "up":
            if row > 0:
                index -= columns
        elif direction == "down":
            if row < rows - 1:
                new_index = index + columns
                if new_index < len(self.versions):
                    index = new_index
                else:
                    index = len(self.versions) - 1

        self._selected_version.set(self.versions[index])
        self._on_version_button_clicked()

    def refresh(self):
        """
        Re-scan /opt/unreal-engine and rebuild the list.
        """
        self._versions = registry.load()
        self._rebuild_versions_scroll_frame()

    def _rebuild_versions_scroll_frame(self):
        """
        Rebuild the grid of version selection buttons.
        """
        for widget in self._scroll_frame.winfo_children():
            widget.destroy()
        self._version_cards.clear()

        if not self._versions:
            Label(self._scroll_frame,
                  text="No Unreal Engine versions found.\nClick 'Get' to download a version, then 'Add' to install it.",
                  justify="left", padding=40, style="List.TLabel").pack(fill="x")
            self._button_launch.config(state="disabled")
            return

        columns = 3
        for i, version in enumerate(self.versions):
            row = Radiobutton(self._scroll_frame, value=version, variable=self._selected_version, text=f"🎮  {version}",
                              command=self._on_version_button_clicked, style="Toolbutton.TRadiobutton")
            row.grid(row=i // columns, column=i % columns, sticky="nsew", padx=4, pady=4)
            self._version_cards[version] = row
            self._bind_status_info(row, f"Select version {version}.")

        for i in range(columns):
            self._scroll_frame.columnconfigure(i, weight=1)

        rows = (len(self.versions) + columns - 1) // columns
        for i in range(rows):
            self._scroll_frame.rowconfigure(i, weight=1)

        # Auto-select first
        self._selected_version.set(self.versions[0])
        self._button_launch.config(state="normal")

    def _on_version_button_clicked(self):
        """
        Handle clicks on version selection radio buttons.
        """
        sel = self._selected_version.get()
        if sel and sel in self._versions:
            self._button_launch.config(state="normal")

    def _on_launch_button_clicked(self):
        """
        Handle clicks on the Launch button.
        """
        sel = self._selected_version.get()
        if not sel:
            return
        version_path = self._versions.get(sel)
        if not version_path or not Path(version_path).exists():
            tk_msgbox_showerror("Not Found", f"The installation directory for '{sel}' no longer exists.")
            self.refresh()
            return
        try:
            unreal.launch_editor(version_path)
            self.quit()
        except FileNotFoundError as e:
            tk_msgbox_showerror("Launch Failed", str(e))
        except Exception as e:
            tk_msgbox_showerror("Launch Failed", f"Unexpected error: {e}")

    def _on_refresh_button_clicked(self):
        """
        Handle clicks on the Refresh button.
        """
        self.refresh()

    def _on_add_button_clicked(self):
        """
        Handle clicks on the Add button to initiate installation.
        """
        zip_path = tk_filedialog_askopenfilename(title="Select Unreal Engine ZIP Archive",
                                                 filetypes=[("ZIP archives", "*.zip"), ("All files", "*.*")],
                                                 initialdir=str(Path.home() / "Downloads"))

        if not zip_path:
            return  # user cancelled

        if not self._ensure_install_root_access():
            return

        self._start_installation(zip_path)

    def _on_remove_button_clicked(self):
        """
        Handle clicks on the Remove button to uninstall a version.
        """
        proceed = tk_msgbox_askyesno(title="Confirmation",
                                     message=f"Are you sure you want to uninstall {self._selected_version.get()}?")
        if not proceed:
            return
        sh_rmtree(f"{INSTALL_ROOT}/{self._selected_version.get()}")
        system.remove_desktop_file(self._selected_version.get())
        self.refresh()

    @staticmethod
    def _ensure_install_root_access():
        """
        Ensure INSTALL_ROOT exists and is writable, asking for admin permission if needed.
        :return: True if the root is accessible, False otherwise.
        """
        if INSTALL_ROOT.exists() and access(INSTALL_ROOT, W_OK):
            return True

        user = getuser()
        install_root = quote(str(INSTALL_ROOT))
        shared_group = quote(SHARED_GROUP)
        quoted_user = quote(user)

        command = (f"mkdir -p {install_root} && "
                   f"chown {quoted_user}:{shared_group} {install_root} && "
                   f"chmod 775 {install_root}")

        try:
            run(["pkexec", "sh", "-c", command], check=True)
        except FileNotFoundError:
            tk_msgbox_showerror(
                "Permission Required",
                "This installation directory requires administrator access, "
                "but 'pkexec' was not found.\n\n"
                "Install PolicyKit/pkexec or create the directory manually.")
            return False
        except CalledProcessError:
            tk_msgbox_showerror(
                "Permission Denied",
                f"Administrator permission was not granted or setup failed:\n{INSTALL_ROOT}")
            return False

        return INSTALL_ROOT.exists() and access(INSTALL_ROOT, W_OK)

    def _on_get_button_clicked(self):
        """
        Open a web browser to the Unreal Engine download page.
        """
        web_open("https://www.unrealengine.com/linux", autoraise=True)  # Some systems might block auto-raise.

    def _start_installation(self, zip_path: str):
        """
        Create the progress window and kick off the extraction thread.
        :param zip_path: Path to the ZIP archive.
        """
        # TODO: get the version number from "./Engine/Build/Build.version" instead of checking the ZIP name.

        version_name = Path(zip_path).stem.split("_")[-1]  # Determine version name from the ZIP filename

        if not all(char.isdigit() or char == "." for char in version_name):
            version_name = Path(zip_path).stem  # Fallback. Unlikely with Epic's naming convention, though.

        for suffix in ("_Linux", "-Linux", "_linux"):  # Strip common suffixes.
            if version_name.endswith(suffix):
                version_name = version_name[: -len(suffix)]
        version_name = version_name.replace(" ", "_")

        target_dir = INSTALL_ROOT / version_name

        if target_dir.exists():
            tk_msgbox_showinfo("No operation!", f"Version '{version_name}' is already installed.")
            return

        dlg = Toplevel(self, background=_COLOR_BG_DARK)
        dlg.title("Installing")
        dlg.geometry("420x200")
        dlg.transient(self)
        dlg.grab_set()
        dlg.resizable(False, False)

        info_label = Label(dlg, text=f"Installing to: {target_dir}", font=("TkDefaultFont", 8), wraplength=380)
        info_label.pack(pady=(16, 8))

        # Progress bar (indeterminate during extraction + setup)
        progress = Progressbar(dlg, mode="determinate", maximum=100, value=0, length=340)
        progress.pack(pady=8)

        status_label = Label(dlg, text="Extracting archive...", font=("TkDefaultFont", 9))
        status_label.pack(pady=(0, 8))

        # Launch extraction in a background thread so the UI stays responsive
        self._install_thread = Thread(
            target=self._extract_and_setup,
            kwargs={"zip_path": zip_path, "target_dir": target_dir, "version_name": version_name, "dialog": dlg,
                    "progress_bar": progress, "status_label": status_label},
            daemon=True)
        self._install_thread.start()

    def _extract_and_setup(self, zip_path: str, target_dir: Path, version_name: str,
                           dialog: Toplevel, progress_bar: Progressbar, status_label: Label):
        """
        Background worker: extract, validate, set permissions, update UI.
        :param zip_path: Path to the ZIP archive.
        :param target_dir: The destination directory.
        :param version_name: The name of the version.
        :param dialog: The progress dialog widget.
        :param progress_bar: The progress bar widget.
        :param status_label: The status label widget.
        """
        # noinspection PyTypeChecker
        try:
            # 1. Create target directory.
            gui.safe_set_text(status_label, "Creating installation directory...")
            INSTALL_ROOT.mkdir(parents=True, exist_ok=True)
            target_dir.mkdir(parents=True, exist_ok=True)

            # 2. Extract ZIP.
            gui.safe_set_text(status_label, "Extracting archive...")
            gui.safe_config(progress_bar, mode="determinate", maximum=100)
            gui.safe_call(progress_bar, "stop")
            gui.safe_set_value(progress_bar, 0)

            with ZipFile(zip_path, "r") as zip_file:
                total = len(zip_file.infolist())
                if total == 0:
                    raise ValueError("The ZIP archive is empty.")
                done = 0

                gui.safe_set_text(status_label, f"Extracting... 0/{total} files (0%)")

                for member in zip_file.infolist():
                    zip_file.extract(member, str(target_dir))
                    done += 1
                    pct = int(done / total * 100)
                    gui.safe_set_value(progress_bar, value=pct)
                    label = f"Extracting... {done}/{total} files ({pct}%)"
                    gui.safe_set_text(status_label, label)

                # 3. Find the actual engine root inside the extract.
                gui.safe_set_text(status_label, "Locating engine folders...")
                engine_root = self._find_engine_root(target_dir)

                # 4. Move into target_dir.
                gui.safe_set_text(status_label, "Moving files to destination...")
                for item in engine_root.iterdir():
                    dest = target_dir / item.name
                    sh_move(str(item), str(dest))

            # 5. Validate.
            gui.safe_set_text(status_label, "Validating installation...")
            gui.safe_call(progress_bar, "stop")
            gui.safe_config(progress_bar, mode="indeterminate")
            gui.safe_call(progress_bar, "start", 25)

            zip.validate_extraction(str(target_dir))

            # 6. Set permissions.
            gui.safe_set_text(status_label, "Setting permissions for shared access...")
            gid = system.get_group_gid()
            uid = system.get_current_user_uid()
            system.set_permissions_recursive(str(target_dir), gid=gid, uid=uid, dir_mode=0o775, file_mode=0o664,
                                             exec_mode=0o775)

            # 7. Ensure executables are marked +x.
            gui.safe_set_text(status_label,
                              "Marking executables...")
            system.set_executable_bits(str(target_dir))

            # 8. Setup DESKTOP shortcut and MIME type.
            system.create_desktop_file(version_name)
            system.create_mime_xml_file()

            # 9. Set complete.
            gui.safe_set_text(status_label, "Success!")
            gui.safe_call(progress_bar, "stop")
            gui.safe_messagebox("Installation Complete",
                                f"Done installing version '{version_name}'.",
                                "info")
            gui.safe_destroy(dialog)
            # noinspection PyTypeChecker
            self.after_idle(self.refresh)

        except ValueError as e:
            gui.safe_call(progress_bar, "stop")
            gui.safe_messagebox("Installation Error", str(e), "error")
            # Cleanup partial install
            sh_rmtree(str(target_dir), ignore_errors=True)
            gui.safe_destroy(dialog)
            # noinspection PyTypeChecker
            self.after_idle(self.refresh)
        except Exception as e:
            gui.safe_call(progress_bar, "stop")
            gui.safe_messagebox(
                "Installation Error",
                f"An unexpected error occurred:\n{e}",
                "error",
            )
            sh_rmtree(str(target_dir), ignore_errors=True)
            gui.safe_destroy(dialog)
            # noinspection PyTypeChecker
            self.after_idle(self.refresh)

    @staticmethod
    def _find_engine_root(extract_dir: str | Path):
        """
        Given the temp extraction directory, find the subfolder that contains the REQUIRED_FOLDERS.
        :param extract_dir: The directory to search.
        :return: The Path to the engine root.
        :raises ValueError: If the engine root cannot be found.
        """
        extract_dir = Path(extract_dir)

        # Check if the root itself has the required folders
        if all((extract_dir / f).exists() for f in REQUIRED_FOLDERS):
            return extract_dir

        # Search one level deep
        for child in extract_dir.iterdir():
            if child.is_dir():
                if all((child / f).exists() for f in REQUIRED_FOLDERS):
                    return child

        # Search two levels deep
        for child in extract_dir.iterdir():
            if child.is_dir():
                for grandchild in child.iterdir():
                    if grandchild.is_dir():
                        if all((grandchild / f).exists() for f in REQUIRED_FOLDERS):
                            return grandchild

        # Could not find — raise so validation gives the error message
        raise ValueError(f"Could not locate the engine root inside the ZIP archive. Expected folders: "
                         + ", ".join(sorted(REQUIRED_FOLDERS))
                         + "\nEnsure you downloaded a valid Unreal Engine Linux ZIP.")

    def _bind_status_info(self, widget, text):
        """
        Bind hover events to update the status bar with the given text.
        :param widget: The widget to bind events to.
        :param text: The text to display in the status bar.
        """

        def on_enter(_):
            self._tooltip_var.set(text)

        def on_leave(_):
            if self._tooltip_var.get() == text:
                self._tooltip_var.set("")

        widget.bind("<Enter>", on_enter)
        widget.bind("<Leave>", on_leave)
