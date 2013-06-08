import sublime
import sublime_plugin
import os
import subprocess
import re

settingsfile = 'Enhanced R.sublime-settings'

class Robject:
    def __init__(self, view):
        self.view = view

    def clean(self, cmd):
        plat = sublime_plugin.sys.platform
        if plat == "darwin":
            cmd = cmd.replace('\\', '\\\\')
            cmd = cmd.replace('"', '\\"')
        cmd = cmd.rstrip('\n')
        if len(re.findall("\n", cmd)) == 0:
            cmd = cmd.strip()
        return cmd

    def rcmd(self, cmd):
        cmd = self.clean(cmd)
        plat = sublime_plugin.sys.platform
        settings = sublime.load_settings(settingsfile)
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
            App = settings.get('linux')['App']
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

class RappSwitcher(sublime_plugin.WindowCommand):

    def show_quick_panel(self, options, done):
        sublime.set_timeout(lambda: self.window.show_quick_panel(options, done), 10)

    def run(self):
        plat = sublime_plugin.sys.platform
        if plat == 'darwin':
            self.app_list = ["R", "R64", "Terminal", "iTerm"]
            pop_string = ["For R 3.x.x, R is 64 bit", "For R version 2.x.x", "Terminal", "iTerm 2"]
        elif plat == "win32":
            self.app_list = ["Ri386", "Rx64"]
            pop_string = ["R i386", "R x64"]
        elif "linux" in plat:
            self.app_list = ["tmux", "screen"]
            pop_string = ["tmux", "screen"]
        else:
            sublime.error_message("Platform not supported!")

        self.show_quick_panel([list(z) for z in zip(self.app_list, pop_string)], self.on_done)

    def on_done(self, action):
        if action==-1: return
        settings = sublime.load_settings(settingsfile)
        plat = sublime_plugin.sys.platform
        if plat == 'darwin':
            plat_setting = settings.get('osx')
            plat_setting['App'] = self.app_list[action]
            settings.set('osx', plat_setting)
        elif plat == "win32":
            plat_setting = settings.get('windows')
            plat_setting['App'] = self.app_list[action]
            settings.set('windows', plat_setting)
        elif "linux" in plat:
            plat_setting = settings.get('linux')
            plat_setting['App'] = self.app_list[action]
            settings.set('linux', plat_setting)
        else:
            sublime.error_message("Platform not supported!")
        sublime.save_settings(settingsfile)
