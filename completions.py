import sublime
import sublime_plugin
import os
import json
import re
from itertools import chain
from .misc import *

def load_jsonfile():
    jsonFilepath = os.path.join(sublime.packages_path(), 'R-Box', 'completions.json')
    jsonFile = open(jsonFilepath, "r", encoding="utf-8")
    data = json.load(jsonFile)
    jsonFile.close()
    return data

def valid(str):
    return re.match('^[\w._]+$', str) is not None

class RBoxCompletions(sublime_plugin.EventListener):
    completions = None
    def on_query_completions(self, view, prefix, locations):
        if not view.match_selector(locations[0], "source.r"):
            return None
        if not RBoxSettings("auto_completions"): return None

        if not self.completions:
            j = dict(load_jsonfile())
            self.completions = list(chain.from_iterable(j.values()))
            self.completions = [(p, ) for p in self.completions if type(p) == str ]

        default_completions = [(item, ) for item in view.extract_completions(prefix) if len(item) > 3 and valid(item)]

        r = list(set(self.completions+default_completions))
        return (r,  0)
