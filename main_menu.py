import sublime
import sublime_plugin
import os
import sys


class RBoxMainMenuListener(sublime_plugin.EventListener):

    def on_activated_async(self, view):
        if view.is_scratch() or view.settings().get('is_widget'):
            return

        targetpath = os.path.join(
            sublime.packages_path(),
            'User', 'R-Box', 'Main.sublime-menu')
        targetdir = os.path.dirname(targetpath)
        point = view.sel()[0].end() if len(view.sel()) > 0 else 0

        psettings = sublime.load_settings('Preferences.sublime-settings')
        if "SendText+" not in psettings.get("ignored_packages", []) and \
                ("SendText+" in sys.modules or "SendTextPlus" in sys.modules) and \
                view.score_selector(
                    point,
                    "source.r, text.tex.latex.rsweave, text.html.markdown.rmarkdown"):

            if not os.path.exists(targetdir):
                os.makedirs(targetdir, 0o755)

            if not os.path.exists(targetpath):
                data = sublime.load_binary_resource(
                    "Packages/R-Box/support/R-Box.sublime-menu")
                with open(targetpath, 'wb') as binfile:
                    binfile.write(data)
                    binfile.close()
        else:
            if os.path.exists(targetpath):
                os.remove(targetpath)


class RBoxMainMenuClearWorkspace(sublime_plugin.TextCommand):
    def run(self, edit):
        ok = sublime.ok_cancel_dialog("Clear R Workspace?")
        if ok:
            self.view.run_command("send_text_plus", {"cmd": "rm(list=ls())"})
