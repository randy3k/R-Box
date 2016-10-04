import sublime
import sublime_plugin
import re

from .util import look_up_packages, load_package_file, function_at_point


class RBoxHintsListener(sublime_plugin.EventListener):
    cache = {}

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
        return settings.get("show_hints", True)

    def popup(self, view, func, point=-1):
        if func in self.cache:
            view.show_popup(
                self.cache[func],
                sublime.COOPERATE_WITH_AUTO_COMPLETE | sublime.HIDE_ON_MOUSE_MOVE_AWAY,
                location=point,
                max_width=600)

    def on_modified_async(self, view):
        if not self.check(view):
            return

        point = view.sel()[0].end() if len(view.sel()) > 0 else 0
        contentb = view.substr(sublime.Region(view.line(point).begin(), point))
        m = re.match(r".*?([a-zA-Z0-9._]+)\($", contentb)
        func = m.group(1) if m else None
        if func:
            self.popup(view, func)
        else:
            view.hide_popup()

    def on_hover(self, view, point, hover_zone):
        sublime.set_timeout_async(lambda: self.on_hover_async(view, point, hover_zone))

    def on_hover_async(self, view, point, hover_zone):
        if not self.check(view):
            return

        settings = sublime.load_settings('R-Box.sublime-settings')
        if not settings.get("show_hints_on_hover", True):
            return

        if hover_zone != sublime.HOVER_TEXT:
            return

        if "meta.function-call.r" not in view.scope_name(point):
            return

        if view.scope_name(point).endswith("variable.function.r "):
            return

        if view.scope_name(point).endswith("support.function.r "):
            return

        func = function_at_point(view, point)
        if func:
            self.popup(view, func, point)
        else:
            view.hide_popup()

    def cache_packages(self, view):
        packages = look_up_packages(view)
        methods = {}

        for pkg in packages:
            j = load_package_file(pkg)
            if j:
                methods.update(j.get("methods"))

        results = view.find_all(r"""\b(?:[a-zA-Z0-9._:]*)\s*(?:<-|=)\s*function\s*"""
                                r"""(\((?:(["\'])(?:[^\\]|\\.)*?\2|#.*$|[^()]|(?1))*\))""")
        for s in results:
            m = re.match(r"^([^ ]+)\s*(?:<-|=)\s*(?:function)\s*(.+)$", view.substr(s))
            if m:
                methods.update({m.group(1): m.group(1)+m.group(2)})

        self.cache.update(methods)

    def on_post_save_async(self, view):
        if self.check(view):
            self.cache_packages(view)

    def on_load_async(self, view):
        if self.check(view):
            self.cache_packages(view)

    def on_activated_async(self, view):
        if self.check(view):
            self.cache_packages(view)
