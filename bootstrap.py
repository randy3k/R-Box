import sublime

version = sublime.version()

if version >= "3000":
    from .rbox import (
        RBoxCompletions,
        RBoxSourcePromptCommand,
        RBoxStatusListener,
        RBoxCleanStatus
    )
else:
    from rbox import (
        RBoxCompletions,
        RBoxSourcePromptCommand,
        RBoxStatusListener,
        RBoxCleanStatus
    )
