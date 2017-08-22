import sublime
import sublime_plugin
import re
from .view_mixin import RBoxViewMixin
from .namespace import namespace_manager
from .settings import r_box_settings


VALIDCOMPLETION = re.compile(r"[.a-zA-Z0-9_-]+$")
VALIDOBJECT = re.compile(r"([a-zA-Z][a-zA-Z0-9.]*)(:::?)([.a-zA-Z0-9_-]*)$")
ARGVALUE = re.compile(r"=\s*[.a-zA-Z0-9_-]*$")


class CompletionMixin:

    default_packages = [
        "base",
        "stats",
        "methods",
        "utils",
        "graphics",
        "grDevices"
    ]

    def filter_completions(self, objects):
        return filter(lambda x: VALIDCOMPLETION.match(x), objects)

    def perpare_pkg_objects(self, pkg):
        ns = namespace_manager.get_namespace(pkg)
        filtered_exported = self.filter_completions(ns.exported)
        return [[obj + "\t{" + pkg + "}", obj] for obj in filtered_exported]

    def get_completions_for_view(self, view):
        return view.settings().get("R-Box.completions", [])

    def set_completions_for_view(self, view, packages):
        # TODO: ultilize loaded_packages to update completions
        completions = []
        packages = list(set(self.default_packages + packages))
        for pkg in packages:
            completions += self.perpare_pkg_objects(pkg)

        completions += [["{}\tInstalled Package".format(pkg), pkg]
                        for pkg in namespace_manager.installed_packages()]

        view.settings().set("R-Box.completions", completions)
        view.settings().set("R-Box.loaded_packages", packages)

    def refresh_completions_for_view(self, view):
        packages = self.inline_packages_for_view(view)
        self.set_completions_for_view(view, packages)

    def get_completions_for_package(self, pkg, exported_only=True):
        ns = namespace_manager.get_namespace(pkg)
        if exported_only:
            return self.filter_completions(ns.exported)
        else:
            return self.filter_completions(ns.unexported)

    def get_function_args(self, pkg, funct):
        return namespace_manager.list_function_args(pkg, funct)

    def preload_package(self, pkg):
        namespace_manager.get_namespace(pkg)


class RBoxCompletionListener(CompletionMixin, RBoxViewMixin, sublime_plugin.ViewEventListener):

    def should_complete(self):
        if self.view.settings().get('is_widget'):
            return False

        point = self.view.sel()[0].end() if len(self.view.sel()) > 0 else 0
        if not self.view.match_selector(point, "source.r, source.r-console"):
            return False

        return r_box_settings.get("auto_completions", True)

    def complete_package_objects(self, pt):
        line = self.extract_line(self.view, pt, truncated=True)
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

        completions = [(item, ) for item in completions if item.startswith(prefix)]
        return (
            completions,
            sublime.INHIBIT_WORD_COMPLETIONS | sublime.INHIBIT_EXPLICIT_COMPLETIONS)

    def complete_function_args(self, pt):
        if ARGVALUE.search(self.extract_line(self.view, pt, truncated=True)):
            return []
        pkg, funct = self.function_name_at_point(self.view, pt)
        if not funct:
            return []
        args = self.get_function_args(pkg, funct)
        return [["{} = \tArguments".format(arg), "{} = ".format(arg)] for arg in args]

    def on_query_completions(self, prefix, locations):
        if not self.should_complete():
            return

        completions = self.complete_package_objects(locations[0])
        if completions:
            return completions

        completions = self.complete_function_args(locations[0])

        completions += self.get_completions_for_view(self.view)
        completions = [item for item in completions if len(item) == 1 or item[1].startswith(prefix)]
        return completions

    def on_post_save_async(self):
        if self.should_complete():
            self.refresh_completions_for_view(self.view)

    def on_load_async(self):
        if self.should_complete():
            self.refresh_completions_for_view(self.view)

    def on_activated_async(self):
        if self.should_complete():
            self.refresh_completions_for_view(self.view)


class RBoxAutoComplete(CompletionMixin, RBoxViewMixin, sublime_plugin.TextCommand):

    def run(self, edit, key=""):
        sublime.set_timeout_async(lambda: self.run_async(key))

    def run_async(self, key):
        if key:
            self.view.run_command("insert_snippet", {"contents": key})

        if key == ":":
            self.view.run_command("hide_auto_complete")
            current_line = self.extract_line(self.view, self.view.sel()[0].end(), truncated=True)
            m = VALIDOBJECT.search(current_line)
            if m:
                pkg, _, _ = m.groups()
                self.preload_package(pkg)

        self.view.run_command("auto_complete")
