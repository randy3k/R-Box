import sublime
import sublime_plugin
import os
import subprocess
import string
import re

########################
#### R Common CLass ####
########################

class RCommon:
    settings = sublime.load_settings('Rsublime.sublime-settings')
    Rapp = settings.get('Rapp')

    def clean(self, str):
        str = string.rstrip(str)
        str = string.replace(str, '\\', '\\\\')
        str = string.replace(str, '"', '\\"')
        return str

    def rcmd(self, cmd, Rapp=None):
        cmd = self.clean(cmd)
        if not Rapp: Rapp = self.Rapp
        if re.match('R', Rapp):
            args = ['osascript']
            args.extend(['-e', 'tell app "' + Rapp + '" to cmd "' + cmd + '"'])
            subprocess.Popen(args)
        elif Rapp == 'Terminal':
            args = ['osascript']
            args.extend(['-e', 'tell app "Terminal" to do script "' + cmd + '" in front window\n'])
            subprocess.Popen(args)

    def set_Rapp(self, Rapp):
        RCommon.Rapp = Rapp
        RCommon.settings.set("Rapp", RCommon.Rapp)
        sublime.save_settings('Rsublime.sublime-settings')

##################################
#### change working directory ####
##################################

class ChangeDirCommand(sublime_plugin.TextCommand, RCommon):
    # read settings only when the instance is created
    # it is more efficient then reading settings everytime when "run" is executed
    def run(self, edit):
        path = os.path.dirname(self.view.file_name())
        cmd = "setwd(\"" + string.replace(path, '"', '\\"') + "\")"
        self.rcmd(cmd)

#########################
#### Send codes to R ####
#########################

class SendSelectCommand(sublime_plugin.TextCommand, RCommon):
    def run(self, edit, **kwargs):
        cmd = ''
        for sel in self.view.sel():
            if sel.empty():
                cmd += self.view.substr(self.view.line(sel)) +'\n'
            else:
                cmd += self.view.substr(sel) +'\n'
        if kwargs.has_key('Rapp'):
            self.rcmd(cmd, kwargs['Rapp'])
        else:
            self.rcmd(cmd)

######################
#### Source codes ####
######################

class SourceCodeCommand(sublime_plugin.TextCommand, RCommon):
    def run(self, edit):
        path = self.view.file_name()
        cmd = "source(\"" + string.replace(path, '"', '\\"') + "\")"
        self.rcmd(cmd)

# Rapp switcher
class RappSwitcher(sublime_plugin.WindowCommand, RCommon):
    app_list = ["R64", "R", "Terminal"]
    def run(self):
        self.window.show_quick_panel(self.app_list, self.on_done)

    def on_done(self, action):
        if action>=0:
            self.set_Rapp(self.app_list[action])
