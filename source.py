import sublime
import sublime_plugin
import os
import re


def listdir(view, dir, base, ext, on_done):
    """List a directory using quick panel"""
    if not os.path.isdir(dir):
        sublime.status_message("Directory %s does not exist." % dir)
        return
    ls = os.listdir(dir)
    if ext:
        fnames = [f for f in ls if os.path.splitext(f)[1].lower() in ext]
    else:
        fnames = [f for f in ls if os.path.isfile(os.path.join(dir, f))]
    if base:
        fnames = [f for f in fnames if base.lower() in f.lower()]

    display = ["[ Create a new file ]", "> "+os.curdir, "> "+os.pardir] + \
        ["> "+f for f in ls if os.path.isdir(os.path.join(dir, f))] + fnames

    def on_action(i):
        if i < 0:
            return
        elif display[i][0] == '>':
            target = display[i][2:] if display[i][0] == '>' else display[i]
            target_dir = os.path.normpath(os.path.join(dir, target))
            sublime.set_timeout(lambda: listdir(view, target_dir, base, ext, on_done), 10)
        elif i == 0:
            view.window().show_input_panel("File: ", "", on_file, None, None)
        else:
            target = os.path.normpath(os.path.join(dir, display[i]))
            on_done(target)

    def on_file(s):
        target = os.path.normpath(os.path.join(dir, s))
        if os.path.exists(target):
            sublime.message_dialog("File %s exists." % target)
            pass
        else:
            target_dir = os.path.dirname(target)
            if not os.path.exists(target_dir):
                os.mkdir(target_dir)
            view.window().open_file(target)
            on_done(target)

    sublime.set_timeout(lambda: view.window().show_quick_panel(display, on_action), 10)


def escape_dq(string):
    string = string.replace('\\', '\\\\')
    string = string.replace('"', '\\"')
    return string


class RBoxSourcePromptCommand(sublime_plugin.TextCommand):

    def run(self, edit):
        view = self.view
        point = view.sel()[0].end() if len(view.sel()) > 0 else 0

        if view.settings().get("auto_match_enabled"):
            view.run_command("insert_snippet", {"contents": "\"${1:$SELECTION}\""})
        else:
            view.run_command("insert", {"characters": "\""})

        fname = view.file_name()
        if not fname:
            return

        sel = view.sel()
        if len(sel) != 1:
            return
        if sel[0].begin() != sel[0].end():
            return
        contentb = view.substr(sublime.Region(view.line(point).begin(), point))
        m = re.match(r".*?(source|sourceCpp)\($", contentb)

        if not m:
            return

        fdir = os.path.dirname(fname)

        def ondone(s):
            s = os.path.relpath(s, fdir)
            view.run_command("insert", {"characters": escape_dq(s)})

        exts = [".r"] if m.group(1) == "source" else [".cpp", ".c", ".c++"]

        listdir(view, fdir, None, exts, ondone)
