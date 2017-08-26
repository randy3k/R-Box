import sublime
import sublime_plugin
import os
import sys
import re


RE_RPROJ = re.compile(".*\.Rproj$")


class RBoxMainMenuListener(sublime_plugin.EventListener):

    def should_show_menu(self, view):

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

        folders = view.window().folders()
        if folders:
            for f in os.listdir(folders[0]):
                if RE_RPROJ.match(f):
                    return True

        return False

    def on_activated_async(self, view):
        if view.settings().get('is_widget'):
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
                with open(targetpath, 'w') as binfile:
                    binfile.write(data)
                    binfile.close()
        else:
            if os.path.exists(targetpath):
                os.remove(targetpath)


class RBoxMainMenuClearWorkspace(sublime_plugin.TextCommand):
    def is_enabled(self):
        return "SendCode" in sys.modules

    def run(self, edit):
        ok = sublime.ok_cancel_dialog("Clear R Workspace?")
        if ok:
            self.view.run_command("send_code", {"cmd": "rm(list=ls())"})
