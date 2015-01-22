import sublime
import sublime_plugin
import json
import re
from itertools import chain
from .misc import RBoxSettings


def load_jsonfile():
    jsonFilepath = "/".join(['Packages', 'R-Box', 'completions.json'])
    data = json.loads(sublime.load_resource(jsonFilepath))
    return data


def valid(str):
    return re.match('^[\w._]+$', str) is not None


class RBoxCompletions(sublime_plugin.EventListener):
    completions = None

    def on_query_completions(self, view, prefix, locations):
        if not view.match_selector(locations[0], "source.r"):
            return None
        if not RBoxSettings("auto_completions"):
            return None

        if True or not self.completions:
            j = dict(load_jsonfile())
            self.completions = list(chain.from_iterable(j.values()))
            self.completions = [item for item in self.completions if type(item) == str]

        completions = [(item,) for item in self.completions if item[0] is prefix]
        default_completions = [(item, ) for item in view.extract_completions(prefix)
                               if len(item) > 3 and valid(item)]

        r = list(set(completions+default_completions))
        return (r, sublime.INHIBIT_WORD_COMPLETIONS)
