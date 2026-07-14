#!/usr/bin/env python3

from importlib import import_module
from tkinter import TclError, Widget, Tk, Toplevel
from tkinter.messagebox import showinfo
from types import NoneType
from typing import Literal, Any, Callable


def _get_root(widget: Widget | NoneType) -> Widget | Tk | Toplevel:
    """
    Get the root widget for the given widget.
    :param widget: The widget to get the root for.
    :return: The root widget.
    """
    if widget is not None:
        try:
            return widget.winfo_toplevel()
        except TclError:
            pass

    # noinspection PyProtectedMember
    return import_module("tkinter")._default_root


def _widget_exists(widget: Widget) -> bool:
    """
    Check if a widget still exists.
    :param widget: The widget to check.
    :return: True if the widget exists, False otherwise.
    """
    try:
        return bool(widget.winfo_exists())
    except TclError:
        return False


def _safe_after(widget: Widget, callback: Callable[[], None]) -> None:
    """
    Safely schedule a callback on the main thread.
    :param widget: The widget to use for scheduling.
    :param callback: The callback function to execute.
    """
    root = _get_root(widget)

    if root is None:
        return

    def guarded_callback() -> None:
        if not _widget_exists(widget):
            return

        try:
            callback()
        except TclError:
            # The widget may have been destroyed after the existence check.
            return

    try:
        # noinspection PyTypeChecker
        root.after(0, guarded_callback)
    except TclError:
        return


def safe_set_text(widget: Any, text: str) -> None:
    """
    Safely set the text of a widget.
    :param widget: The widget to modify.
    :param text: The text to set.
    """
    _safe_after(widget, lambda: widget.config(text=text))


def safe_set_value(widget: Any, value: Any) -> None:
    """
    Safely set the value of a widget.
    :param widget: The widget to modify.
    :param value: The value to set.
    """
    _safe_after(widget, lambda: widget.config(value=value))


def safe_config(widget: Any, **kwargs: Any) -> None:
    """
    Safely configure a widget.
    :param widget: The widget to configure.
    :param kwargs: The configuration arguments.
    """
    _safe_after(widget, lambda: widget.config(**kwargs))


def safe_call(widget: Any, method_name: str, *args: Any) -> None:
    """
    Safely call a method on a widget.
    :param widget: The widget to call the method on.
    :param method_name: The name of the method to call.
    :param args: The arguments to pass to the method.
    """
    _safe_after(widget, lambda: getattr(widget, method_name)(*args))


def safe_messagebox(title: str, message: str, icon: Literal["error", "info", "question", "warning"]) -> None:
    """
    Safely show a message box.
    :param title: The title of the message box.
    :param message: The message to display.
    :param icon: The icon to show.
    """
    root = _get_root(None)

    if root is None:
        return

    try:
        # noinspection PyTypeChecker
        root.after(0, lambda: showinfo(title, message, icon=icon))
    except TclError:
        return


def safe_destroy(dialog: Any) -> None:
    """
    Safely destroy a dialog widget.
    :param dialog: The dialog widget to destroy.
    """
    root = _get_root(dialog)

    if root is None:
        return

    def guarded_destroy() -> None:
        if not _widget_exists(dialog):
            return

        try:
            dialog.destroy()
        except TclError:
            return

    try:
        # noinspection PyTypeChecker
        root.after(0, guarded_destroy)
    except TclError:
        return
