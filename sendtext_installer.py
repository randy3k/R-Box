import sublime
import sys


def plugin_loaded():
    if "SendText+" not in sys.modules and "package_control" in sys.modules:
        ok = sublime.ok_cancel_dialog("R-Box requires SendText+, install it now?")
        if ok:
            sublime.active_window().run_command(
                "advanced_install_package", {"packages": "SendText+"})
