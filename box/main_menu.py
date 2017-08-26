import sublime
import sublime_plugin
import os
import threading


_main_menu_is_visible = [False]


def main_menu_is_visible():
    return _main_menu_is_visible[0]


class RBoxMainMenuListener(sublime_plugin.EventListener):
    _window_is_rproject = []
    _window_is_not_rproject = []

    def window_is_rproj(self, folder):
        for f in os.listdir(folder):
            if f.endswith(".Rproj"):
                return True

    def is_r_project(self, window):
        if not window:
            return False
        folders = window.folders()
        if window.id() in self._window_is_rproject:
            return True
        elif window.id() not in self._window_is_not_rproject and folders:
            if self.window_is_rproj(folders[0]):
                self._window_is_rproject.append(window.id())
                return True
            else:
                self._window_is_not_rproject.append(window.id())
                return False

    def is_r_file(self, view):
        try:
            pt = view.sel()[0].end()
        except:
            pt = 0

        if view.match_selector(
                pt,
                "source.r, "
                "text.tex.latex.rsweave, "
                "text.html.markdown.rmarkdown, "
                "source.c++.rcpp"):
            return True

        return False

    def on_activated_async(self, view):
        if view.settings().get('is_widget'):
            return
        if hasattr(self, "timer") and self.timer:
            self.timer.cancel()

        def set_main_menu():

            menu_path = os.path.join(
                        sublime.packages_path(),
                        'User', 'R-Box', 'Main.sublime-menu')
            menu_dir = os.path.dirname(menu_path)

            if self.is_r_project(view.window()) or self.is_r_file(view):

                if not os.path.exists(menu_dir):
                    os.makedirs(menu_dir, 0o755)

                if not os.path.exists(menu_path):
                    data = sublime.load_resource(
                        "Packages/R-Box/support/R-Box.sublime-menu")
                    with open(menu_path, 'w') as binfile:
                        binfile.write(data)
                        binfile.close()
                _main_menu_is_visible[0] = True
            else:
                if os.path.exists(menu_path):
                    os.remove(menu_path)
                _main_menu_is_visible[0] = False

        self.timer = threading.Timer(0.1, set_main_menu)
        self.timer.start()

    def on_query_context(self, view, key, operator, operand, match_all):
        if view.settings().get('is_widget'):
            return

        if key == "r_box.main_menu_is_visible":
            out = _main_menu_is_visible[0] == operand
            return out if operator == 0 else not out
