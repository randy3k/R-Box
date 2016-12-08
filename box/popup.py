import sublime
import sublime_plugin
import mdpopups
from .mixins import RBoxMixins
from .completion import completion_manager
from .namespace import namespace_manager


POPUP_TEMPLATE = """{}[Help]({}:::{})"""


class RBoxPopupListener(sublime_plugin.ViewEventListener, RBoxMixins):

    def should_show_popup(self):
        if self.view.settings().get('is_widget'):
            return False

        point = self.view.sel()[0].end() if len(self.view.sel()) > 0 else 0
        if not self.view.match_selector(point, "source.r, source.r-console"):
            return False

        return self.rbox_settings("show_popup_hints", True)

    def popup(self, text, point=-1):
        mdpopups.show_popup(
            self.view,
            text,
            flags=sublime.COOPERATE_WITH_AUTO_COMPLETE | sublime.HIDE_ON_MOUSE_MOVE_AWAY,
            location=point,
            max_width=800,
            on_navigate=self.on_help)

    def on_help(self, package):
        pkg, funct = package.split(":::")
        self.view.window().run_command(
            "open_url",
            {"url": "http://www.rdocumentation.org/packages/{}/topics/{}".format(pkg, funct)})

    def on_hover(self, point, hover_zone):
        sublime.set_timeout_async(lambda: self.on_hover_async(point, hover_zone))

    def on_hover_async(self, point, hover_zone):
        if not self.should_show_popup():
            return
        if hover_zone != sublime.HOVER_TEXT:
            return

        pkg, funct = self.function_name_at_point(self.view, point)
        if not funct:
            return
        if not pkg:
            pkg = namespace_manager.find_object_in_packages(funct)
        funct_call = namespace_manager.get_function_call(pkg, funct)
        if not funct_call:
            return

        pref_settings = sublime.load_settings("Preferences.sublime-settings")
        use_sublime_highlighter = pref_settings.get("mdpopups.use_sublime_highlighter", True)
        sublime_user_lang_map = pref_settings.get("sublime_user_lang_map", {})
        pref_settings.set("mdpopups.use_sublime_highlighter", True)
        pref_settings.set(
            "mdpopups.sublime_user_lang_map",
            {"s": [["r"], ["R-Box/syntax/R Extended"]]})

        self.popup(POPUP_TEMPLATE.format(
            mdpopups.syntax_highlight(self.view, funct_call.strip(), language="r"),
            pkg,
            funct), point)

        def reset_vs():
            pref_settings.set("mdpopups.use_sublime_highlighter", use_sublime_highlighter)
            pref_settings.set("mdpopups.sublime_user_lang_map", sublime_user_lang_map)

        sublime.set_timeout_async(reset_vs, 1000)
