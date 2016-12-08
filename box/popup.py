import sublime
import sublime_plugin
import mdpopups
from .mixins import RBoxMixins
from .namespace import namespace_manager
from .utils import preference_temporary_settings


POPUP_TEMPLATE = """{}[Help](help:{}:::{}) [Replace](replace:)"""


class RBoxPopupListener(sublime_plugin.ViewEventListener, RBoxMixins):

    def should_show_popup(self):
        if self.view.settings().get('is_widget'):
            return False

        point = self.view.sel()[0].end() if len(self.view.sel()) > 0 else 0
        if not self.view.match_selector(point, "source.r, source.r-console"):
            return False

        return self.rbox_settings("show_popup_hints", True)

    def function_popup(self, pkg, funct, point=-1):
        funct_call = namespace_manager.get_function_call(pkg, funct)
        if not funct_call:
            return
        self._funct_call = " ".join([x.strip() for x in funct_call.split("\n")])
        self._point = point
        with preference_temporary_settings("mdpopups.use_sublime_highlighter", True):
            with preference_temporary_settings(
                    "mdpopups.sublime_user_lang_map",
                    {"s": [["r"], ["R-Box/syntax/R Extended"]]}):
                text = POPUP_TEMPLATE.format(
                        mdpopups.syntax_highlight(self.view, funct_call.strip(), language="r"),
                        pkg,
                        funct)
                mdpopups.show_popup(
                    self.view,
                    text,
                    flags=sublime.COOPERATE_WITH_AUTO_COMPLETE | sublime.HIDE_ON_MOUSE_MOVE_AWAY,
                    location=point,
                    max_width=800,
                    on_navigate=self.on_navigate)

    def on_navigate(self, link):
        command, option = link.split(":", 1)
        if command == "help":
            pkg, funct = option.split(":::")
            self.view.window().run_command(
                "open_url",
                {"url": "http://www.rdocumentation.org/packages/{}/topics/{}".format(pkg, funct)})

        elif command == "replace":
            self.replace_function_at_point(self.view, self._point, self._funct_call)
            self.view.run_command("hide_popup")

    def on_hover(self, point, hover_zone):
        sublime.set_timeout_async(lambda: self.on_hover_async(point, hover_zone))

    def on_hover_async(self, point, hover_zone):
        if not self.should_show_popup():
            return
        if hover_zone != sublime.HOVER_TEXT:
            return

        pkg, funct = self.function_name_at_point(self.view, point)
        if funct:
            if not pkg:
                pkg = namespace_manager.find_object_in_packages(funct)
            self.function_popup(pkg, funct, point)
