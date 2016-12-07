import sublime
import os
import re
import subprocess
if sublime.platform() == "windows":
    from winreg import OpenKey, QueryValueEx, HKEY_LOCAL_MACHINE, KEY_READ


def read_registry(key, valueex):
    reg_key = OpenKey(HKEY_LOCAL_MACHINE, key, 0, KEY_READ)
    return QueryValueEx(reg_key, valueex)


ANSI_ESCAPE = re.compile(r'(\x9B|\x1B\[)[0-?]*[ -/]*[@-~]')


def execute_command(cmd, **kwargs):
    if sublime.platform() == "windows":
        # make sure console does not come up
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    else:
        startupinfo = None

    out = subprocess.check_output(
        cmd, startupinfo=startupinfo, **kwargs).decode("utf-8")

    return ANSI_ESCAPE.sub('', out)


class OutputPanel:

    def __init__(
        self, name, file_regex='', line_regex='', base_dir=None,
        word_wrap=False, line_numbers=False, gutter=False,
        scroll_past_end=False, syntax='Packages/Text/Plain text.tmLanguage'
    ):
        self.name = name
        self.window = sublime.active_window()
        self.output_view = self.window.get_output_panel(name)

        # default to the current file directory
        if (not base_dir and self.window.active_view() and
                self.window.active_view().file_name()):
            base_dir = os.path.dirname(self.window.active_view().file_name())

        settings = self.output_view.settings()
        settings.set("result_file_regex", file_regex)
        settings.set("result_line_regex", line_regex)
        settings.set("result_base_dir", base_dir)
        settings.set("word_wrap", word_wrap)
        settings.set("line_numbers", line_numbers)
        settings.set("gutter", gutter)
        settings.set("scroll_past_end", scroll_past_end)
        settings.set("syntax", syntax)
        self.closed = False

    def write(self, s):
        sublime.set_timeout(
            lambda: self.output_view.run_command('output_panel_insert', {'characters': s}),
            10)

    def writeln(self, s):
        self.write(s + "\n")

    def flush(self):
        pass

    def show(self):
        self.window.run_command("show_panel", {"panel": "output." + self.name})

    def close(self):
        self.closed = True
        pass
