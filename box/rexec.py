import sublime_plugin
from .settings import r_box_settings
from .script_mixin import ScriptMixin


def escape_dquote(cmd):
    cmd = cmd.replace('\\', '\\\\')
    cmd = cmd.replace('"', '\\"')
    return cmd


def escape_squote(cmd):
    cmd = cmd.replace('\\', '\\\\')
    cmd = cmd.replace("\'", "\'")
    return cmd


def replace_variable(cmd, var, value):
    cmd = cmd.replace("\"" + var + "\"", "\"" + escape_dquote(value) + "\"")
    cmd = cmd.replace("'" + var + "'", "'" + escape_squote(value) + "'")
    return cmd.replace(var, value)


class RBoxExecCommand(ScriptMixin, sublime_plugin.WindowCommand):
    def run(self, cmd, cwd=None):
        if cwd:
            working_dir = cwd
        else:
            working_dir = self.find_working_dir()

        custom_env = self.custom_env()

        extracted_variables = self.window.extract_variables()
        for var, value in extracted_variables.items():
            cmd = replace_variable(cmd, "$"+var, value)

        self.window.run_command(
            "exec",
            {
                "cmd": [r_box_settings.rscript_binary(), "-e", cmd],
                "working_dir": working_dir,
                "env": {"PATH": custom_env["PATH"]}
            })
