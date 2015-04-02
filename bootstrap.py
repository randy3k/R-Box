import sublime

version = sublime.version()

if version >= "3000":
    from .rbox import (
        RBoxCompletions,
        RBoxSendSelectionCommand, RBoxChangeDirCommand,
        RBoxSourceCodeCommand, RSendSelectCommand,
        RBoxAppSwitchCommand,
        RBoxSourcePromptCommand,
        RBoxStatusListener, RBoxCleanStatus,
        update_resources
    )
else:
    from rbox import (
        RBoxCompletions,
        RBoxSendSelectionCommand, RBoxChangeDirCommand,
        RBoxSourceCodeCommand, RSendSelectCommand,
        RBoxAppSwitchCommand,
        RBoxSourcePromptCommand,
        RBoxStatusListener, RBoxCleanStatus,
        update_resources
    )


def plugin_loaded():
    if sublime.platform() == "windows":
        update_resources("AutoHotkeyU32.exe")
        update_resources("Rgui.ahk")
        update_resources("Cmder.ahk")
        update_resources("Cygwin.ahk")

if sublime.version() < '3000':
    plugin_loaded()
