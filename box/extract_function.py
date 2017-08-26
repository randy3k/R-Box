import sublime
import sublime_plugin
import re

from .rscript import ScriptMixin
from .namespace import namespace_manager


class RBoxExtractFunctionCommand(ScriptMixin, sublime_plugin.TextCommand):
    def run(self, edit, func_name=None):
        if "codetools" not in namespace_manager.installed_packages():
            print("R-Box: package `codetools` is not installed.")
            return

        if not func_name:
            self.view.window().show_input_panel(
                "Function name:", "",
                lambda x: self.view.run_command("r_box_extract_function", {"func_name": x}),
                None, None)
            return

        sels = self.view.sel()
        if len(sels) == 0 or len(sels) > 1:
            return

        region = self.view.sel()[0]
        indentation = re.match(r"^\s*", self.view.substr(self.view.line(region.begin()))).group(0)

        if region.empty():
            code = self.view.substr(self.view.line(region.begin()))
        else:
            code = self.view.substr(sublime.Region(
                    self.view.line(region.begin()).begin(),
                    self.view.line(region.end()).end()
                ))
        try:
            free_vars = self.detect_free_vars(code)

            self.view.insert(
                edit,
                self.view.line(region.end()).end(),
                "\n{}}}\n".format(indentation))

            self.view.insert(
                edit,
                self.view.line(region.begin()).begin(),
                "{}{} <- function({}) {{\n".format(indentation, func_name, ", ".join(free_vars)))

            self.view.run_command("indent")
            sublime.status_message("Extract function successed.")

        except:
            sublime.status_message("Extract function failed.")
