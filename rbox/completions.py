import sublime
import sublime_plugin
import json
import re
import os
from itertools import chain


def load_jsonfile():
    if sublime.version() < '3000':
        jsonFilepath = os.path.join(sublime.packages_path(),
                                    'R-Box', 'support', 'completions.json')
        data = None
        with open(jsonFilepath, "r") as f:
            data = json.load(f)
    else:
        jsonFilepath = "/".join(['Packages', 'R-Box', 'support', 'completions.json'])
        data = json.loads(sublime.load_resource(jsonFilepath))
    return data


class RBoxCompletions(sublime_plugin.EventListener):
    completions = None

    def on_query_completions(self, view, prefix, locations):
        settings = sublime.load_settings('R-Box.sublime-settings')
        if not view.match_selector(locations[0], "source.r, source.r-console"):
            return None
        if not settings.get("auto_completions"):
            return None

        if not self.completions:
            j = dict(load_jsonfile())
            self.completions = list(chain.from_iterable(j.values()))

        completions = [(item, item) for item in self.completions if prefix in item]

        r = list(set(completions))
        return r
