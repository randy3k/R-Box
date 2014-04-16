import sublime
import sublime_plugin
import os
import json
from itertools import chain
from .misc import *

def load_jsonfile():
    jsonFilepath = os.path.join(sublime.packages_path(), 'R-Box', 'completions.json')
    jsonFile = open(jsonFilepath, "r", encoding="utf-8")
    data = json.load(jsonFile)
    jsonFile.close()
    return data

class RBoxCompletions(sublime_plugin.EventListener):
    completions = None
    def on_query_completions(self, view, prefix, locations):
        if not view.match_selector(locations[0], "source.r"):
            return None
        if not RBoxSettings("auto_completions"): return None

        default_completions = [(item, item) for sublist in [view.extract_completions(prefix)]
            for item in sublist if len(item) > 3]
        default_completions = list(set(default_completions))

        if not self.completions:
            j = dict(load_jsonfile())
            self.completions = list(chain.from_iterable(j.values()))
            self.completions = [(p, p) for p in self.completions if type(p) == str ]
        return (self.completions+default_completions,
            sublime.INHIBIT_WORD_COMPLETIONS | sublime.INHIBIT_EXPLICIT_COMPLETIONS)

