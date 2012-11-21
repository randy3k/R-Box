import sublime
import sublime_plugin
import os
import subprocess
import string

########################
#### R Common CLass ####
########################

class RCommon:
    settings = sublime.load_settings('Rsublime.sublime-settings')
    Rapp = settings.get('Rapp')

    def clean(self, str):
        str = string.replace(str, '\\', '\\\\')
        str = string.replace(str, '"', '\\"')
        return str

    def rcmd(self, cmd):
        cmd = self.clean(cmd)
        args = ['osascript']
        args.extend(['-e', 'tell app \"' + self.Rapp + '\" to cmd \"' + cmd + '\"'])
        subprocess.Popen(args)        

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
    def run(self, edit):
        str = ''
        for sel in self.view.sel():
            if sel.empty():
                str += self.view.substr(self.view.line(sel)) +'\n'
            else:
                str += self.view.substr(sel) +'\n'
        self.rcmd(str)

######################
#### Source codes ####
######################

class SourceCodeCommand(sublime_plugin.TextCommand, RCommon):
    def run(self, edit):
        path = self.view.file_name()
        cmd = "source(\"" + string.replace(path, '"', '\\"') + "\")"
        self.rcmd(cmd)
################################
#### Send Codes to Terminal ####
################################

class SendSelectTerminalCommand(sublime_plugin.TextCommand, RCommon):
       def run(self, edit):
        str = ''
        for sel in self.view.sel():
            if sel.empty():
                str += self.view.substr(self.view.line(sel)) +'\n'
            else:
                str += self.view.substr(sel) +'\n'
        str = self.clean(str)
        args = ['osascript']
        args.extend(['-e', 'tell app "Terminal" to do script "' + str + '" in front window\n'])
        subprocess.Popen(args)
