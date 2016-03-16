import sublime
import sublime_plugin
import json
import os
import re


def load_jsonfile(pkg):
    data = None

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


class RBoxCompletions(sublime_plugin.EventListener):
    completions = {}

    def check(self, view):
        if view.is_scratch() or view.settings().get('is_widget'):
            return False

        point = view.sel()[0].end() if len(view.sel()) > 0 else 0
        if not view.match_selector(point, "source.r, source.r-console"):
            return False

        settings = sublime.load_settings('R-Box.sublime-settings')
        return settings.get("auto_completions", True)

    def on_query_completions(self, view, prefix, locations):
        if not self.check(view):
            return

        vid = view.id()
        if vid not in self.completions:
            sublime.set_timeout_async(lambda: self.loaded_libraries(view), 100)
            return

        completions = [item for item in self.completions[vid] if prefix in item[1]]

        return completions

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
        objects = []
        for pkg in packages:
            j = load_jsonfile(pkg)
            if j:
                for obj in j.get("objects"):
                    objects.append((obj + "\t{" + pkg + "}", obj))

        vid = view.id()
        self.completions[vid] = objects

    def on_post_save(self, view):
        if self.check(view):
            sublime.set_timeout_async(lambda: self.loaded_libraries(view), 100)

    def on_load(self, view):
        if self.check(view):
            sublime.set_timeout_async(lambda: self.loaded_libraries(view), 100)

    def on_activated(self, view):
        if self.check(view):
            sublime.set_timeout_async(lambda: self.loaded_libraries(view), 100)
