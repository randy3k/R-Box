import sublime
import sublime_plugin
import os
import subprocess
import re

# A Common Class
class RCommon:
    Rapplist = None

    def clean(self, cmd):
        cmd = cmd.strip()
        cmd = cmd.replace('\\', '\\\\')
        cmd = cmd.replace('"', '\\"')
        return cmd

    def rcmd(self, cmd, which=0):
        if RCommon.Rapplist == None: self.get_Rapp()
        cmd = self.clean(cmd)
        Rapp = RCommon.Rapplist[which]
        if re.match('R', Rapp):
            args = ['osascript']
            args.extend(['-e', 'tell app "' + Rapp + '" to cmd "' + cmd + '"'])
            subprocess.Popen(args)
        elif Rapp == 'Terminal':
            args = ['osascript']
            args.extend(['-e', 'tell app "Terminal" to do script "' + cmd + '" in front window\n'])
            subprocess.Popen(args)
        elif Rapp == 'iTerm':
                args = ['osascript']
                apple_script = ('tell application "' + Rapp + '"\n'
                                    'tell the first terminal\n'
                                        'tell current session\n'
                                            'write text "' + cmd + '"\n'
                                        'end tell\n'
                                    'end tell\n'
                                'end tell\n')
                args.extend(['-e', apple_script])
                subprocess.Popen(args)

    def set_Rapp(self, which, Rapp):
        if RCommon.Rapplist == None: self.get_Rapp()
        RCommon.Rapplist[which] = Rapp

    def get_Rapp(self):
        self.settings = sublime.load_settings('Rsublime.sublime-settings')
        RCommon.Rapplist = self.settings.get('Rapp')
        if RCommon.Rapplist == None:
                RCommon.Rapplist = ["R", "Terminal"]

    def save_settings(self):
        self.settings.set("Rapp", RCommon.Rapplist)
        sublime.save_settings('Rsublime.sublime-settings')

class ChangeDirCommand(sublime_plugin.TextCommand, RCommon):
    def run(self, edit):
        path = os.path.dirname(self.view.file_name())
        cmd = "setwd(\"" + self.clean(path) + "\")"
        self.rcmd(cmd)


class SendSelectCommand(sublime_plugin.TextCommand, RCommon):
    def expand_sel(self, sel):
        esel = self.view.find(r"""^.*(\{(?:(["\'])(?:[^\\\\]|\\\\.|\n)*?\\2|#.*$|[^\{\}]|\n|(?1))*\})"""
            , self.view.line(sel).begin())
        if self.view.line(sel).begin() == esel.begin():
            return esel

    def run(self, edit, which):
        cmd = ''
        for sel in self.view.sel():
            if sel.empty():
                thiscmd = self.view.substr(self.view.line(sel))
                if re.match(r".*\{\s*$", thiscmd):
                    esel = self.expand_sel(sel)
                    if esel:
                        thiscmd = self.view.substr(esel)
            else:
                thiscmd = self.view.substr(sel)
                if self.view.score_selector(sel.end()-1, "meta.function.r") and \
                    not self.view.score_selector(sel.end(), "meta.function.r"):
                    esel = self.expand_sel(sel)
                    if esel:
                        thiscmd = self.view.substr(esel)
            cmd += thiscmd +'\n'

        self.rcmd(cmd, which)

class SourceCodeCommand(sublime_plugin.TextCommand, RCommon):
    def run(self, edit):
        path = self.view.file_name()
        cmd = "source(\"" +  self.clean(path) + "\")"
        self.rcmd(cmd)

class RappSwitcher(sublime_plugin.WindowCommand, RCommon):
    app_list = ["R", "R64", "Terminal", "iTerm"]
    msg = ["Choose your Primary Rapp", "Choose your Secondary Rapp"]
    pop_string = ["R", "R64 (for R 2.x.x)", "Terminal", "iTerm 2"]

    def show_quick_panel(self, options, done):
        sublime.set_timeout(lambda: self.window.show_quick_panel(options, done), 10)

    def run(self, which):
        self.which = which
        self.show_quick_panel([self.msg[which]]+ self.pop_string, self.on_done)

    def on_done(self, action):
        if action>=1:
            self.set_Rapp(self.which, self.app_list[action-1])
            self.save_settings()

