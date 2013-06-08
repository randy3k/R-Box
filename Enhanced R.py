import sublime
import sublime_plugin
import os
import subprocess
import re

class Robject:
    def __init__(self, view):
        self.view = view

    def clean(self, cmd):
        plat = sublime_plugin.sys.platform
        cmd = cmd.rstrip('\n')
        if len(re.findall("\n", cmd)) == 0:
            cmd = cmd.strip()
        if plat == "darwin" or "linux" in plat:
            cmd = cmd.replace('\\', '\\\\')
            cmd = cmd.replace('"', '\\"')
            cmd = cmd.rstrip('\n')
        elif plat == "windows":
            pass
        return cmd

    def rcmd(self, cmd):
        cmd = self.clean(cmd)
        plat = sublime_plugin.sys.platform
        settings = sublime.load_settings('Enhanced R.sublime-settings')
        if plat == 'darwin':
            App = settings.get('osx')['App']
            if re.match('R', App):
                args = ['osascript']
                args.extend(['-e', 'tell app "' + App + '" to cmd "' + cmd + '"'])
                subprocess.Popen(args)
            elif App == 'Terminal':
                args = ['osascript']
                args.extend(['-e', 'tell app "Terminal" to do script "' + cmd + '" in front window\n'])
                subprocess.Popen(args)
            elif App == 'iTerm':
                    args = ['osascript']
                    apple_script = ('tell application "' + App + '"\n'
                                        'tell the first terminal\n'
                                            'tell current session\n'
                                                'write text "' + cmd + '"\n'
                                            'end tell\n'
                                        'end tell\n'
                                    'end tell\n')
                    args.extend(['-e', apple_script])
                    subprocess.Popen(args)

        elif plat == 'win32':
            App = settings.get('windows')['App']
            if App == "Rx64":
                progpath = settings.get('windows')['Rx64']
                if not progpath: progpath = "1"
            elif App == "Ri386":
                progpath = settings.get('windows')['Ri386']
                if not progpath: progpath = "0"

            ahk_path = os.path.join(sublime.packages_path(), 'Enhanced-R', 'bin','AutoHotkey')
            ahk_script_path = os.path.join(sublime.packages_path(), 'Enhanced-R', 'bin','R.ahk')
            # manually add "\n" to keep the indentation of first line of block code
            args = [ahk_path, ahk_script_path, progpath, "\n"+cmd ]
            subprocess.Popen(args)

        elif 'linux' in plat:
            if App == "tmux":
                progpath = settings.get('linux')['tmux']
                if not progpath: progpath = 'tmux'

                subprocess.call([progpath, 'set-buffer', selection])
                subprocess.call([progpath, 'paste-buffer', '-d'])

            elif App == "screen":
                progpath = settings.get('linux')['screen']
                if not progpath: progpath = 'screen'

                subprocess.call([progpath, '-X', 'stuff', selection])
        else:
            sublime.error_message("Platform not supported!")

#     def set_Rapp(self, which, Rapp):
#         if RCommon.Rapplist == None: self.get_Rapp()
#         RCommon.Rapplist[which] = Rapp

#     def get_Rapp(self):
#         settings = sublime.load_settings('Rsublime.sublime-settings')
#         RCommon.Rapplist = settings.get('Rapp')
#         if RCommon.Rapplist == None:
#                 RCommon.Rapplist = ["R", "Terminal"]

#     def save_settings(self):
#         settings = sublime.load_settings('Rsublime.sublime-settings')
#         settings.set("Rapp", RCommon.Rapplist)
#         sublime.save_settings('Rsublime.sublime-settings')

def pathclean(path):
    path = path.strip()
    path = path.replace('\\', '\\\\')
    path = path.replace('"', '\\"')
    return path

class RSendSelectCommand(sublime_plugin.TextCommand):
    def expand_sel(self, sel):
        esel = self.view.find(r"""^.*(\{(?:(["\'])(?:[^\\\\]|\\\\.|\n)*?\\2|#.*$|[^\{\}]|\n|(?1))*\})"""
            , self.view.line(sel).begin())
        if self.view.line(sel).begin() == esel.begin():
            return esel

    def run(self, edit):
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

        R = Robject(self.view)
        R.rcmd(cmd)


class RChangeDirCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        path = os.path.dirname(self.view.file_name())
        cmd = "setwd(\"" + pathclean(path) + "\")"
        R = Robject(self.view)
        R.rcmd(cmd)

class RSourceCodeCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        path = self.view.file_name()
        cmd = "source(\"" +  pathclean(path) + "\")"
        R = Robject(self.view)
        R.rcmd(cmd)

# class RappSwitcher(sublime_plugin.WindowCommand, RCommon):
#     app_list = ["R", "R64", "Terminal", "iTerm"]
#     msg = ["Choose your Primary Rapp", "Choose your Secondary Rapp"]
#     pop_string = ["R", "R64 (for R 2.x.x)", "Terminal", "iTerm 2"]

#     def show_quick_panel(self, options, done):
#         sublime.set_timeout(lambda: self.window.show_quick_panel(options, done), 10)

#     def run(self, which):
#         self.which = which
#         self.show_quick_panel([self.msg[which]]+ self.pop_string, self.on_done)

#     def on_done(self, action):
#         if action>=1:
#             self.set_Rapp(self.which, self.app_list[action-1])
#             self.save_settings()

