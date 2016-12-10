import sublime
import sublime_plugin
import threading
import mdpopups
from .mixins import RBoxMixins
from .namespace import namespace_manager
from .utils import preference_temporary_settings


POPUP_TEMPLATE = """{}[Help](help:{}:::{}) [Paste](paste:)"""


class RBoxShowPopup(RBoxMixins, sublime_plugin.TextCommand):
    def run(self, edit, pkg, funct, point=-1):
        sublime.set_timeout_async(
            lambda: self.run_async(pkg, funct, point))

    def run_async(self, pkg, funct, point=-1):
        if not funct:
            pkg, funct = self.function_name_at_point(self.view, point)
        if not pkg:
            pkg = namespace_manager.find_object_in_packages(funct)
        funct_call = namespace_manager.get_function_call(pkg, funct)
        if not funct_call:
            return
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
                    on_navigate=lambda x: self.on_navigate(x, pkg, funct, point))

    def on_navigate(self, link, pkg, funct, point):
        command, option = link.split(":", 1)
        if command == "help":
            pkg, funct = option.split(":::")
            self.view.window().run_command(
                "open_url",
                {"url": "http://www.rdocumentation.org/packages/{}/topics/{}".format(pkg, funct)})

        elif command == "paste":
            self.replace_function_at_point(self.view, point)
            self.view.run_command("hide_popup")


class RBoxPopupListener(RBoxMixins, sublime_plugin.ViewEventListener):
    thread = None

    def should_show_popup(self):
        if self.view.settings().get('is_widget'):
            return False

        point = self.view.sel()[0].end() if len(self.view.sel()) > 0 else 0
        if not self.view.match_selector(point, "source.r, source.r-console"):
            return False

        return self.r_box_settings("show_popup_hints", True)

    def on_hover(self, point, hover_zone):
        sublime.set_timeout_async(lambda: self.on_hover_async(point, hover_zone))

    def on_hover_async(self, point, hover_zone):
        if not self.should_show_popup():
            return
        if hover_zone != sublime.HOVER_TEXT:
            return

        self.view.run_command(
            "r_box_show_popup", {
                "pkg": None,
                "funct": None,
                "point": point
            })

    def on_modified_async(self):
        if not self.should_show_popup():
            return
        if self.thread:
            self.thread.cancel()
            self.thread = None

        sel = self.view.sel()
        if len(sel) == 0 or not sel[0].empty():
            return
        point = self.view.sel()[0].end()
        if self.view.substr(sublime.Region(point-1, point)) is not "(":
            return
        if not self.view.match_selector(point-2, "meta.function-call.r"):
            return
        self.thread = threading.Timer(
            2,
            lambda: self.view.run_command(
                "r_box_show_popup", {
                    "pkg": None,
                    "funct": None,
                    "point": point-1
                })
        )
        self.thread.start()
