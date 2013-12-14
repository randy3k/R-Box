import sublime
import sublime_plugin
import os
import json
import codecs


def load_jsonfile():
    jsonFilepath = os.path.join(sublime.packages_path(), 'Enhanced-R', 'support', 'completions.json')
    jsonFile = codecs.open(jsonFilepath, "r", encoding="utf-8")
    print(jsonFilepath)
    data = json.load(jsonFile)
    jsonFile.close()
    return data

class RCompletions(sublime_plugin.EventListener):
    completions = None
    def on_query_completions(self, view, prefix, locations):
        if not view.match_selector(locations[0], "source.r"):
            return None
        if not view.settings().get("r_auto_completions"): return None

        point = locations[0]
        if not self.completions: self.completions = load_jsonfile()['completions']
        r = [(p,p) for p in self.completions if type(p) == str ]
        return (r,  sublime.INHIBIT_WORD_COMPLETIONS | sublime.INHIBIT_EXPLICIT_COMPLETIONS)

