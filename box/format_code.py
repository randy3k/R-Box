import sublime
import sublime_plugin
import re

from .rscript import ScriptMixin
from .namespace import namespace_manager


class RBoxFormatCodeCommand(ScriptMixin, sublime_plugin.TextCommand):
    def run(self, edit):
        if "formatR" not in namespace_manager.installed_packages():
            print("R-Box: package `formatR` is not installed.")
            return

        width = self.view.settings().get('wrap_width')
        if not width or width == 0:
            rulers = self.view.settings().get("rulers")
            width = rulers[0] if rulers else 100

        tab_size = self.view.settings().get("tab_size", 4)

        for region in reversed(self.view.sel()):
            indentation = re.match(
                r"^\s*", self.view.substr(self.view.line(region.begin()))).group(0)

            if region.empty():
                region = self.view.line(region.begin())

            code = self.view.substr(region)
            try:
                if code:
                    formatted_code = self.format_code(
                        code,
                        indent=tab_size,
                        width_cutoff=width-len(indentation)-20)

                    formatted_code = "\n".join(
                        [indentation + l.rstrip() if len(l.strip()) > 0 else ""
                         for l in formatted_code.split("\n")])

                    self.view.run_command(
                        "r_box_replace_selection",
                        {"region": (region.begin(), region.end()), "text": formatted_code})
            except:
                sublime.status_message("Format code failed.")
                return

            sublime.status_message("Format code successed.")
