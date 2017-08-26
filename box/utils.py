import sublime
import sublime_plugin
import os
from contextlib import contextmanager

if sublime.platform() == "windows":
    from winreg import OpenKey, QueryValueEx, HKEY_LOCAL_MACHINE, KEY_READ


def read_registry(key, valueex):
    reg_key = OpenKey(HKEY_LOCAL_MACHINE, key, 0, KEY_READ)
    return QueryValueEx(reg_key, valueex)


@contextmanager
def preference_temporary_settings(key, value, timeout=0):
    pref_settings = sublime.load_settings("Preferences.sublime-settings")
    old_value = pref_settings.get(key)
    pref_settings.set(key, value)
    yield
    sublime.set_timeout(
        lambda: pref_settings.set(key, old_value), timeout)


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


class RBoxReplaceSelectionCommand(sublime_plugin.TextCommand):

    def run(self, edit, region, text):
        self.view.replace(edit, sublime.Region(region[0], region[1]), text)


def escape_dquote(cmd):
    cmd = cmd.replace('\\', '\\\\')
    cmd = cmd.replace('"', '\\"')
    return cmd
