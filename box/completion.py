import sublime
import sublime_plugin
import re
from .view_mixin import RBoxViewMixin
from .namespace import namespace_manager
from .settings import r_box_settings

VALIDOBJECT = re.compile(r"([a-zA-Z][a-zA-Z0-9.]*)(:::?)([.a-zA-Z0-9_-]*)$")
ARGVALUE = re.compile(r"=\s*[.a-zA-Z0-9_-]*$")


class RBoxCompletionListener(RBoxViewMixin, sublime_plugin.EventListener):
    def should_complete(self, view):
        if view.settings().get('is_widget'):
            return False

        try:
            pt = view.sel()[0].end()
        except Exception:
            pt = 0

        if not view.match_selector(pt, "source.r, source.r-console"):
            return False

        return r_box_settings.get("auto_completions", True)

    def get_function_args(self, pkg, funct):
        return namespace_manager.list_function_args(pkg, funct)

    def get_completions_for_package(self, pkg, exported_only=True):
        ns = namespace_manager.get_namespace(pkg)
        if exported_only:
            return self.filter_completions(ns.exported)
        else:
            return self.filter_completions(ns.unexported)

    def complete_package_objects(self, view, pt):
        line = self.extract_line(view, pt, truncated=True)
        m = VALIDOBJECT.search(line)
        if not m:
            return []
        pkg, delim, prefix = m.groups()

        if delim == "::":
            completions = self.get_completions_for_package(
                pkg, exported_only=True)
        elif delim == ":::":
            completions = self.get_completions_for_package(
                pkg, exported_only=False)
        else:
            return []

        completions = [(item, ) for item in completions
                       if item.startswith(prefix)]
        return (completions, sublime.INHIBIT_WORD_COMPLETIONS
                | sublime.INHIBIT_EXPLICIT_COMPLETIONS)

    def complete_function_args(self, view, pt):
        if ARGVALUE.search(self.extract_line(view, pt, truncated=True)):
            return []
        pkg, funct = self.function_name_at_point(view, pt)
        if not funct:
            return []
        args = self.get_function_args(pkg, funct)
        return [["{} = \tArguments".format(arg), "{} = ".format(arg)]
                for arg in args]

    def get_completions_for_view(self, view):
        return view.settings().get("R-Box.completions", [])


    def on_query_completions(self, view, prefix, locations):
        if not self.should_complete(view):
            return

        completions = self.complete_package_objects(view, locations[0])
        if completions:
            return completions

        completions = self.complete_function_args(view, locations[0])

        completions += self.get_completions_for_view(view)
        completions = [
            item for item in completions
            if len(item) == 1 or item[1].startswith(prefix)
        ]
        return completions


class RBoxAutoComplete(RBoxViewMixin, sublime_plugin.TextCommand):
    def run(self, edit, key=""):
        sublime.set_timeout_async(lambda: self.run_async(key))

    def run_async(self, key):
        if key:
            self.view.run_command("insert_snippet", {"contents": key})

        if key == ":":
            self.view.run_command("hide_auto_complete")
            current_line = self.extract_line(
                self.view, self.view.sel()[0].end(), truncated=True)
            m = VALIDOBJECT.search(current_line)
            if m:
                pkg, _, _ = m.groups()
                self.preload_package(pkg)

        self.view.run_command("auto_complete")

    def preload_package(self, pkg):
        namespace_manager.get_namespace(pkg)
