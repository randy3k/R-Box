import sublime, sublime_plugin
import os
import re
from . misc import *

class RBoxSourcePromptCommand(sublime_plugin.TextCommand):

    def run(self, edit):
        view = self.view
        point = view.sel()[0].end() if len(view.sel())>0 else 0
        if not view.score_selector(point, "source.r"):
            return
        fname = view.file_name()
        if not fname: return

        this_row = view.rowcol(point)[0]
        sel = view.sel()
        if len(sel)!=1: return
        if sel[0].begin() != sel[0].end(): return
        contentb = view.substr(sublime.Region(view.line(point).begin(), point))
        m = re.match(r".*?(source|sourceCpp)\($", contentb)
        if view.settings().get("auto_match_enabled"):
            view.run_command("insert_snippet", {"contents": "\"${1:$SELECTION}\""})
        else:
            view.run_command("insert", {"characters" : "\""})

        if not m: return

        fdir = os.path.dirname(fname)
        def ondone(s):
            s = os.path.relpath(s, fdir)
            view.run_command("insert", {"characters" : escape_dq(s)})
        exts = [".r"] if m.group(1) == "source" else [".cpp", ".c", ".c++"]

        listdir(view, fdir, None, exts, ondone)
