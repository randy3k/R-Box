import sublime_plugin
import re

from .rscript import ScriptMixin
from .namespace import namespace_manager


class RBoxFormatCodeCommand(ScriptMixin, sublime_plugin.TextCommand):
    def run(self, edit):
        if "formatR" not in namespace_manager.installed_packages():
            print("R-Box: package `formatR` is not installed.")
            return

        for region in reversed(self.view.sel()):
            indentation = re.match(
                r"^\s*", self.view.substr(self.view.line(region.begin()))).group(0)

            if region.empty():
                region = self.view.line(region.begin())

            code = self.view.substr(region)
            if code:
                try:
                    formatted_code = self.format_code(code)
                except:
                    print("R-Box: cannot format this chunk of code.")
                    return

                formatted_code = "\n".join([indentation + l for l in formatted_code.split("\n")])
                self.view.run_command(
                    "r_box_replace_selection",
                    {"region": (region.begin(), region.end()), "text": formatted_code})
