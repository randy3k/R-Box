import sublime
import sublime_plugin
from .settings import r_box_settings
from .script_mixin import ScriptMixin


class RBoxExecCommand(ScriptMixin, sublime_plugin.WindowCommand):
    def run(self, cmd, cwd=None):
        if cwd:
            working_dir = cwd
        else:
            working_dir = self.find_working_dir()

        custom_env = self.custom_env()

        extracted_variables = self.window.extract_variables()
        cmd = sublime.expand_variables(cmd, extracted_variables)

        self.window.run_command(
            "exec",
            {
                "cmd": [r_box_settings.rscript_binary(), "-e", cmd],
                "working_dir": working_dir,
                "env": {"PATH": custom_env["PATH"]}
            })


class RBoxKillExecCommand(sublime_plugin.WindowCommand):
    def run(self):
        self.window.run_command("cancel_build")
        self.window.run_command("exec", {"kill": True})
