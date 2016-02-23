import sublime
import sys


def plugin_loaded():
    rsettings = sublime.load_settings('R-Box.sublime-settings')
    psettings = sublime.load_settings('Preferences.sublime-settings')

    if not rsettings.get("show_sendtext_installer_message", True):
        return

    if "SendText+" in psettings.get("ignored_packages", []):
        return

    if "SendText+" in sys.modules:
        return

    if "package_control" not in sys.modules:
        return

    ok = sublime.ok_cancel_dialog(
        "R-Box: Sending code feature requires \"SendText+\", install it now?")
    if ok:
        sublime.active_window().run_command(
            "advanced_install_package", {"packages": "SendText+"})
