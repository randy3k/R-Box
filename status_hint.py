import sublime
import sublime_plugin
import re
import json
import os

if sublime.version() < '3000':
    set_timeout = sublime.set_timeout
else:
    set_timeout = sublime.set_timeout_async


def load_jsonfile():
    if sublime.version() < '3000':
        jsonFilepath = os.path.join(sublime.packages_path(),
                                    'R-Box', 'support', 'hint.json')
        data = None
        with open(jsonFilepath, "r") as f:
            data = json.load(f)
    else:
        jsonFilepath = "/".join(['Packages', 'R-Box', 'support', 'hint.json'])
        data = json.loads(sublime.load_resource(jsonFilepath))
    return data


class RBoxStatusListener(sublime_plugin.EventListener):
    cache = {}
    last_row = 0

    def check(self, view):
        if view.is_scratch() or view.settings().get('is_widget'):
            return False
        point = view.sel()[0].end() if len(view.sel()) > 0 else 0
        if not view.score_selector(point, "source.r"):
            return False
        settings = sublime.load_settings('R-Box.sublime-settings')
        return settings.get("status_bar_hint", True)

    def update_status(self, view):
        if not self.check(view):
            return

        if not self.cache:
            self.cache = dict(load_jsonfile())

        point = view.sel()[0].end() if len(view.sel()) > 0 else 0
        this_row = view.rowcol(point)[0]
        sel = view.sel()
        if len(sel) != 1:
            return
        if sel[0].begin() != sel[0].end():
            return
        contentb = view.substr(sublime.Region(view.line(point).begin(), point))
        m = re.match(r".*?([a-zA-Z0-9.]+)\($", contentb)
        if not m:
            return
        view.set_status("r_box", "")
        func = m.group(1)

        if func in self.cache:
            call = self.cache[func]
            self.last_row = this_row
            view.set_status("r_box", call)
            view.settings().set("r_box_status", True)

    def capture_functions(self, view):
        if not self.cache:
            self.cache = dict(load_jsonfile())
        funcsel = view.find_all(r"""\b(?:[a-zA-Z0-9._:]*)\s*(?:<-|=)\s*function\s*"""
                                r"""(\((?:(["\'])(?:[^\\]|\\.)*?\2|#.*$|[^()]|(?1))*\))""")
        for s in funcsel:
            m = re.match(r"^([^ ]+)\s*(?:<-|=)\s*(?:function)\s*(.+)$", view.substr(s))
            if m:
                self.cache.update({m.group(1): m.group(1)+m.group(2)})

    def on_selection_modified(self, view):
        if self.check(view):
            point = view.sel()[0].end() if len(view.sel()) > 0 else 0
            this_row = view.rowcol(point)[0]
            if this_row != self.last_row:
                view.set_status("r_box", "")
                view.settings().set("r_box_status", False)

    def on_modified(self, view):
        if self.check(view):
            set_timeout(lambda: self.update_status(view), 1)

    def on_post_save(self, view):
        if self.check(view):
            set_timeout(lambda: self.capture_functions(view), 1)

    def on_load(self, view):
        if self.check(view):
            set_timeout(lambda: self.capture_functions(view), 1)

    def on_activated(self, view):
        if self.check(view):
            set_timeout(lambda: self.capture_functions(view), 1)


class RBoxCleanStatus(sublime_plugin.TextCommand):
    def run(self, edit):
        view = self.view
        view.set_status("r_box", "")
        view.settings().set("r_box_status", False)
