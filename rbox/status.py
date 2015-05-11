import sublime
import sublime_plugin
import re
import json
import os

if sublime.version() < '3000':
    set_timeout = sublime.set_timeout
else:
    set_timeout = sublime.set_timeout_async


def load_jsonfile(pkg):
    data = None
    if sublime.version() < '3000':
        jsonFilepath = os.path.join(sublime.packages_path(),
                                    'R-Box', 'packages', '%s.json' % pkg)
        if os.path.exists(jsonFilepath):
            with open(jsonFilepath, "r") as f:
                data = json.load(f)
    else:
        jsonFilepath = "/".join(['Packages', 'R-Box', 'packages', '%s.json' % pkg])
        try:
            data = json.loads(sublime.load_resource(jsonFilepath))
        except IOError:
            pass

    if data:
        return data

    jsonFilepath = os.path.join(sublime.packages_path(), "User",
                                'R-Box', 'packages', '%s.json' % pkg)
    if os.path.exists(jsonFilepath):
        with open(jsonFilepath, "r") as f:
            data = json.load(f)

    return data


class RBoxStatusListener(sublime_plugin.EventListener):
    cache = {}
    last_row = 0

    def check(self, view):
        if view.is_scratch() or view.settings().get('is_widget'):
            return False

        sel = view.sel()
        if len(sel) != 1:
            return

        if sel[0].begin() != sel[0].end():
            return

        point = sel[0].end() if len(sel) > 0 else 0
        if not view.score_selector(point, "source.r"):
            return False

        settings = sublime.load_settings('R-Box.sublime-settings')
        return settings.get("status_bar_hint", True)

    def on_selection_modified(self, view):
        if self.check(view):
            point = view.sel()[0].end() if len(view.sel()) > 0 else 0
            this_row = view.rowcol(point)[0]
            if this_row != self.last_row:
                view.set_status("r_box", "")
                view.settings().set("r_box_status", False)

    def on_modified(self, view):
        if self.check(view):
            set_timeout(lambda: self.update_status(view), 100)

    def update_status(self, view):
        vid = view.id()
        if vid not in self.cache:
            return
        point = view.sel()[0].end() if len(view.sel()) > 0 else 0
        this_row = view.rowcol(point)[0]
        contentb = view.substr(sublime.Region(view.line(point).begin(), point))
        m = re.match(r".*?([a-zA-Z0-9._]+)\($", contentb)
        if not m:
            return
        view.set_status("r_box", "")
        func = m.group(1)

        if func in self.cache[vid]:
            call = self.cache[vid][func]
            self.last_row = this_row
            view.set_status("r_box", call)
            view.settings().set("r_box_status", True)

    def loaded_libraries(self, view):
        packages = [
            "base",
            "stats",
            "methods",
            "utils",
            "graphics",
            "grDevices"
        ]
        for s in [view.substr(s) for s in view.find_all("(?:library|require)\(([^)]*?)\)")]:
            m = re.search(r"""\((?:"|')?(.*?)(?:"|')?\)""", s)
            if m:
                packages.append(m.group(1))

        packages = list(set(packages))
        methods = {}
        for pkg in packages:
            j = load_jsonfile(pkg)
            if j:
                methods.update(j.get("methods"))

        results = view.find_all(r"""\b(?:[a-zA-Z0-9._:]*)\s*(?:<-|=)\s*function\s*"""
                                r"""(\((?:(["\'])(?:[^\\]|\\.)*?\2|#.*$|[^()]|(?1))*\))""")
        for s in results:
            m = re.match(r"^([^ ]+)\s*(?:<-|=)\s*(?:function)\s*(.+)$", view.substr(s))
            if m:
                methods.update({m.group(1): m.group(1)+m.group(2)})

        vid = view.id()
        self.cache[vid] = methods

    def on_post_save(self, view):
        if self.check(view):
            set_timeout(lambda: self.loaded_libraries(view), 100)

    def on_load(self, view):
        if self.check(view):
            set_timeout(lambda: self.loaded_libraries(view), 100)

    def on_activated(self, view):
        if self.check(view):
            set_timeout(lambda: self.loaded_libraries(view), 100)


class RBoxCleanStatus(sublime_plugin.TextCommand):
    def run(self, edit):
        view = self.view
        view.set_status("r_box", "")
        view.settings().set("r_box_status", False)
