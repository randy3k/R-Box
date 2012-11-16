import sublime
import sublime_plugin
import os
import subprocess
import string

###############################
#### Some useful functions ####
###############################

def clean(str):
    str = string.replace(str, '\\', '\\\\')
    str = string.replace(str, '"', '\\"')
    str = string.replace(str, '\'', '\\\\\'')
    return str


##################################
#### change working directory ####
##################################

class ChangeDirCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        path = clean(os.path.dirname(self.view.file_name()))
        args = ['osascript']
        args.extend(['-e', 'tell app "R64" to cmd "setwd(\'' + path + '\')"\n'])
        subprocess.Popen(args)

#########################
#### Send codes to R ####
#########################

class SendSelectCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        str = ''
        for sel in self.view.sel():
            if sel.empty():
                str += self.view.substr(self.view.line(sel)) +'\n'
            else:
                str += self.view.substr(sel) +'\n'
        str = clean(str)
        args = ['osascript']
        args.extend(['-e','tell app "R64" to cmd "' + str +'"\n'])
        subprocess.Popen(args)

######################
#### Source codes ####
######################

class SourceCodeCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        path = clean(self.view.file_name())
        args = ['osascript']
        args.extend(['-e', 'tell app "R64" to cmd "source(\'' + path + '\')"\n'])
        subprocess.Popen(args)
