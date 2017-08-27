import sublime_plugin
import os
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

    def resolve(self, cmd):
        view = self.window.active_view()
        file = view.file_name()
        if file:
            file_name = os.path.basename(file)
            file_path = os.path.dirname(file)
            file_base_name, file_ext = os.path.splitext(file_name)
            cmd = replace_variable(cmd, "$file_path", file_path)
            cmd = replace_variable(cmd, "$file_name", file_name)
            cmd = replace_variable(cmd, "$file_base_name", file_base_name)
            cmd = replace_variable(cmd, "$file_extension", file_ext)
            cmd = replace_variable(cmd, "$file", file)

        if len(view.sel()) == 1:
            row, _ = view.rowcol(view.sel()[0].begin())
            cmd = replace_variable(cmd, "$line", str(row+1))

        if view.window():
            pd = view.window().project_data()
            if pd and "folders" in pd and len(pd["folders"]) > 0:
                folder = pd["folders"][0].get("path")
                if folder:
                    cmd = replace_variable(cmd, "$folder", folder)

            pfn = view.window().project_file_name()
            if pfn:
                project_path = os.path.dirname(file)
                cmd = replace_variable(cmd, "$project_path", project_path)

        if len(view.sel()) == 1:
            word = view.substr(view.sel()[0])
            if not word:
                word = view.substr(view.word(view.sel()[0].begin()))

            cmd = replace_variable(cmd, "$selection", word)

        return cmd

    def run(self, cmd, cwd=None):
        if cwd:
            working_dir = cwd
        else:
            working_dir = self.find_working_dir()

        custom_env = self.custom_env()

        cmd = self.resolve(cmd)

        self.window.run_command(
            "exec",
            {
                "cmd": [r_box_settings.rscript_binary(), "-e", cmd],
                "working_dir": working_dir,
                "env": {"PATH": custom_env["PATH"]}
            })
