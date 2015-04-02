import sublime

version = sublime.version()

__all__ = [
    "RBoxAppSwitchCommand",
    "RBoxCompletions",
    "RBoxSendSelectionCommand", "RBoxChangeDirCommand",
    "RBoxSourceCodeCommand", "RSendSelectCommand",
    "RBoxSourcePromptCommand",
    "RBoxStatusListener", "RBoxCleanStatus",
    "update_resources"
]

if version >= "3000":
    from .rbox import (
        RBoxAppSwitchCommand,
        RBoxCompletions,
        RBoxSendSelectionCommand, RBoxChangeDirCommand,
        RBoxSourceCodeCommand, RSendSelectCommand,
        RBoxSourcePromptCommand,
        RBoxStatusListener, RBoxCleanStatus,
        update_resources
    )
else:
    from rbox import (
        RBoxAppSwitchCommand,
        RBoxCompletions,
        RBoxSendSelectionCommand, RBoxChangeDirCommand,
        RBoxSourceCodeCommand, RSendSelectCommand,
        RBoxSourcePromptCommand,
        RBoxStatusListener, RBoxCleanStatus,
        update_resources
    )


if sublime.platform() == "windows":

    def plugin_loaded():
        update_resources("AutoHotkeyU32.exe")
        update_resources("Rgui.ahk")
        update_resources("Cmder.ahk")
        update_resources("Cygwin.ahk")

    __all__.append("plugin_loaded")

    if sublime.version() < '3000':
        plugin_loaded()
