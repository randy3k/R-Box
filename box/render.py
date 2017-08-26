import sublime_plugin
import os
from .utils import escape_dquote


class RBoxRenderRmarkdownCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        file_name = self.view.file_name()
        file_path = os.path.dirname(file_name)
        cmd = "rmarkdown::render(\"{}\", encoding = \"UTF-8\")".format(escape_dquote(file_name))
        self.view.window().run_command(
            "r_box_exec",
            {"cmd": cmd, "cwd": file_path}
        )


class RBoxSweaveRnwCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        file_name = self.view.file_name()
        file_path = os.path.dirname(file_name)
        file_base_name = os.path.splitext(file_name)[0]
        cmd = "Sweave(\"{}\");tools::texi2dvi(\"{}.tex\", pdf = TRUE)".format(
                    escape_dquote(file_path),
                    escape_dquote(file_name),
                    escape_dquote(file_base_name)
            )
        self.view.window().run_command(
            "r_box_exec",
            {"cmd": cmd, "cwd": file_path}
        )


class RBoxKnitRnwCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        file_name = self.view.file_name()
        file_path = os.path.dirname(file_name)
        file_base_name = os.path.splitext(file_name)[0]
        cmd = ("knitr::knit(\"{}\", output=\"{}.tex\");" +
               "tools::texi2dvi(\"{}.tex\", pdf = TRUE)").format(
                    escape_dquote(file_name),
                    escape_dquote(file_base_name),
                    escape_dquote(file_base_name)
            )
        self.view.window().run_command(
            "r_box_exec",
            {"cmd": cmd, "cwd": file_path}
        )
