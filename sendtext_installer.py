import sublime
import sys


def plugin_loaded():
    rsettings = sublime.load_settings('R-Box.sublime-settings')
    ssettings = sublime.load_settings('SendText+.sublime-settings')
    psettings = sublime.load_settings('Preferences.sublime-settings')

    if not rsettings.get("show_sendtext_installer_message", True):
        return

    if "SendText+" in psettings.get("ignored_packages", []) or \
            "SendTextPlus" in psettings.get("ignored_packages", []):
        return

    if "SendText+" in sys.modules or "SendTextPlus" in sys.modules:
        return

    if "package_control" not in sys.modules:
        return

    ok = sublime.ok_cancel_dialog(
        "R-Box: \"SendTextPlus\" is missing, "
        "sending code feature requires \"SendTextPlus\". Install it now?")
    if ok:
        prog = rsettings.get("prog")
        if prog:
            ssettings.set("prog", prog)
            sublime.save_settings('SendText+.sublime-settings')
        sublime.active_window().run_command(
            "advanced_install_package", {"packages": "SendTextPlus"})
