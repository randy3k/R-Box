import sublime
import sublime_plugin

from .util import look_up_packages, load_package_file


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
        packages = look_up_packages(view)
        objects = []

        for pkg in packages:
            j = load_package_file(pkg)
            if j:
                for obj in j.get("objects"):
                    objects.append((obj + "\t{" + pkg + "}", obj))

        vid = view.id()
        self.completions[vid] = objects

    def on_post_save_async(self, view):
        if self.check(view):
            self.loaded_libraries(view)

    def on_load_async(self, view):
        if self.check(view):
            self.loaded_libraries(view)

    def on_activated_async(self, view):
        if self.check(view):
            self.loaded_libraries(view)
