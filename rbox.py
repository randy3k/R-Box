from .box.completion import RBoxCompletionListener, RBoxAutoComplete
from .box.popup import RBoxPopupListener, RBoxShowPopup
from .box.main_menu import RBoxMainMenuListener, RBoxMainMenuClearWorkspace
from .box.source_prompt import RBoxSourcePromptCommand
from .box.linter import install_linter_spec
from .box.format_code import RBoxFormatCodeCommand
from .box.extract_function import RBoxExtractFunctionCommand
from .box.utils import RBoxReplaceSelectionCommand


def plugin_loaded():
    install_linter_spec()
