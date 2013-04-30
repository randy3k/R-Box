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
        if self.Rapplist == None: self.get_Rapp()
        cmd = self.clean(cmd)
        Rapp = self.Rapplist[which]
        if re.match('R', Rapp):
            args = ['osascript']
            args.extend(['-e', 'tell app "' + Rapp + '" to cmd "' + cmd + '"'])
            subprocess.Popen(args)
        elif Rapp == 'Terminal':
            args = ['osascript']
            args.extend(['-e', 'tell app "Terminal" to do script "' + cmd + '" in front window\n'])
            subprocess.Popen(args)

    def set_Rapp(self, which, Rapp):
        if self.Rapplist == None: self.get_Rapp()
        self.Rapplist[which] = Rapp

    def get_Rapp(self):
        self.settings = sublime.load_settings('Rsublime.sublime-settings')
        self.Rapplist = self.settings.get('Rapp')
        if self.Rapplist == None:
                self.Rapplist = ["R", "Terminal"]

    def save_settings(self):
        self.settings.set("Rapp", self.Rapplist)
        sublime.save_settings('Rsublime.sublime-settings')

class ChangeDirCommand(sublime_plugin.TextCommand, RCommon):
    def run(self, edit):
        path = os.path.dirname(self.view.file_name())
        cmd = "setwd(\"" + self.clean(path) + "\")"
        self.rcmd(cmd)


class SendSelectCommand(sublime_plugin.TextCommand, RCommon):
    def run(self, edit, which):
        cmd = ''
        for sel in self.view.sel():
            if sel.empty():
                cmd += self.view.substr(self.view.line(sel)) +'\n'
            else:
                cmd += self.view.substr(sel) +'\n'

        # save for later use
        # '^.*(\{(?:(["\'])(?:[^\\\\]|\\\\.|\n)*?\\2|#.*$|[^\{\}]|\n|(?1))*\})'
        self.rcmd(cmd, which)

class SourceCodeCommand(sublime_plugin.TextCommand, RCommon):
    def run(self, edit):
        path = self.view.file_name()
        cmd = "source(\"" +  self.clean(path) + "\")"
        self.rcmd(cmd)

class RappSwitcher(sublime_plugin.WindowCommand, RCommon):
    app_list = ["R", "R64", "Terminal"]
    pop_string = ["R", "R64 (for R 2.x.x)", "Terminal"]

    def show_quick_panel(self, options, done):
        sublime.set_timeout(lambda: self.window.show_quick_panel(options, done), 10)

    def run(self):
        self.show_quick_panel(["Choose your primary Rapp"]+ self.pop_string, self.on_done)

    def on_done(self, action):
        if action>=1:
            self.set_Rapp(0, self.app_list[action-1])
            self.show_quick_panel(["Choose your secondary Rapp"]+ self.pop_string, self.on_done2)

    def on_done2(self, action):
        if action>=1:
            self.set_Rapp(1, self.app_list[action-1])
        self.save_settings()
