import sublime
import sublime_plugin
import os
import subprocess
import re

import sys
if sys.version >= '3':
    string = str
else:
    import string

########################
#### R Common CLass ####
########################

class RCommon:
    settings = sublime.load_settings('Rsublime.sublime-settings')
    if settings.has('Rapp'):
        Rapplist = settings.get('Rapp')
    else:
        Rapplist = None
    if not Rapplist:
        Rapplist = ["R64", "Terminal"]
    if Rapplist != settings.get('Rapp'):
        sublime.save_settings('Rsublime.sublime-settings')

    def clean(self, cmd):
        cmd = string.strip(cmd)
        cmd = string.replace(cmd, '\\', '\\\\')
        cmd = string.replace(cmd, '"', '\\"')
        return cmd

    def rcmd(self, cmd, which=0):
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
        RCommon.Rapplist[which] = Rapp

    def save_settings(self):
        self.settings.set("Rapp", RCommon.Rapplist)
        sublime.save_settings('Rsublime.sublime-settings')

##################################
#### change working directory ####
##################################

class ChangeDirCommand(sublime_plugin.TextCommand, RCommon):
    # read settings only when the instance is created
    # it is more efficient then reading settings everytime when "run" is executed
    def run(self, edit):
        path = os.path.dirname(self.view.file_name())
        cmd = "setwd(\"" + self.clean(path) + "\")"
        self.rcmd(cmd)

#########################
#### Send codes to R ####
#########################

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

######################
#### Source codes ####
######################

class SourceCodeCommand(sublime_plugin.TextCommand, RCommon):
    def run(self, edit):
        path = self.view.file_name()
        cmd = "source(\"" +  self.clean(path) + "\")"
        self.rcmd(cmd)

# Rapp switcher

class RappSwitcher(sublime_plugin.WindowCommand, RCommon):
    app_list = ["R64", "R", "Terminal"]

    def show_quick_panel(self, options, done):
        sublime.set_timeout(lambda: self.window.show_quick_panel(options, done), 10)

    def run(self):
        self.show_quick_panel(["Choose your primary Rapp"]+ self.app_list, self.on_done)

    def on_done(self, action):
        if action>=1:
            self.set_Rapp(0, self.app_list[action-1])
            self.show_quick_panel(["Choose your secondary Rapp"]+ self.app_list, self.on_done2)

    def on_done2(self, action):
        if action>=1:
            self.set_Rapp(1, self.app_list[action-1])
        self.save_settings()
