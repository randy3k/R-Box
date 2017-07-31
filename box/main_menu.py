import sublime
import sublime_plugin
import os
import sys
import re


class RBoxMainMenuListener(sublime_plugin.EventListener):

    def send_repl_installed(self):
        return "SendREPL" in sys.modules

    def send_text_plus_installed(self):
        return "SendTextPlus" in sys.modules

    def should_show_menu(self, view):

        sel = [s for s in view.sel()]
        point = sel[0].end() if len(sel) > 0 else 0
        score = view.score_selector(
            point,
            "source.r, "
            "text.tex.latex.rsweave, "
            "text.html.markdown.rmarkdown, "
            "source.c++.rcpp")

        if score > 0:
            return True

        r = re.compile(".*\.Rproj$")
        try:
            pd = view.window().project_data()
            first_folder = pd["folders"][0]["path"]
            for f in os.listdir(first_folder):
                if r.match(f):
                    return True
        except:
            pass

        return False

    def on_activated_async(self, view):
        if view.is_scratch() or view.settings().get('is_widget'):
            return

        targetpath = os.path.join(
            sublime.packages_path(),
            'User', 'R-Box', 'Main.sublime-menu')
        targetdir = os.path.dirname(targetpath)

        if self.should_show_menu(view):

            if not os.path.exists(targetdir):
                os.makedirs(targetdir, 0o755)

            if not os.path.exists(targetpath):
                data = sublime.load_binary_resource(
                    "Packages/R-Box/support/R-Box.sublime-menu").decode("utf-8")
                if not self.send_repl_installed() and self.send_text_plus_installed():
                    # fall back to send_text_plus
                    data = data.replace("send_repl", "send_text_plus")
                with open(targetpath, 'w') as binfile:
                    binfile.write(data)
                    binfile.close()
        else:
            if os.path.exists(targetpath):
                os.remove(targetpath)


class RBoxMainMenuClearWorkspace(sublime_plugin.TextCommand):
    def run(self, edit):
        ok = sublime.ok_cancel_dialog("Clear R Workspace?")
        if ok:
            if "SendREPL" in sys.modules:
                self.view.run_command("send_repl", {"cmd": "rm(list=ls())"})
            elif "SendTextPlus" in sys.modules:
                self.view.run_command("send_text_plus", {"cmd": "rm(list=ls())"})
