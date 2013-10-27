import sublime
import sublime_plugin
import os
import subprocess
import re

settingsfile = 'Enhanced-R.sublime-settings'

# escape double quote
def escape_dq(string):
    string = string.replace('\\', '\\\\')
    string = string.replace('"', '\\"')
    return string

# clean command before sending to R
def clean(cmd):
    plat = sublime.platform()
    if plat == "osx":
        cmd = escape_dq(cmd)
    cmd = cmd.rstrip('\n')
    if len(re.findall("\n", cmd)) == 0:
        cmd = cmd.lstrip()
    return cmd

# get platform specific key
def get_setting(key, default=None):
    plat = sublime.platform()
    settings = sublime.load_settings(settingsfile)
    plat_settings = settings.get(plat)
    if key in plat_settings:
        return plat_settings[key]
    else:
        return default

# the main function
def rcmd(cmd):
    cmd = clean(cmd)
    plat = sublime.platform()
    if plat == 'osx':
        App = get_setting("App", "R")
        if re.match('R', App):
            args = ['osascript']
            args.extend(['-e', 'tell app "' + App + '" to cmd "' + cmd + '"'])
            subprocess.Popen(args)
        elif App == 'Terminal':
            args = ['osascript']
            args.extend(['-e', 'tell app "Terminal" to do script "' + cmd + '" in front window\n'])
            subprocess.Popen(args)
        elif re.match('iTerm', App):
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

    elif plat == 'windows':
        App = get_setting("App", "R64")
        progpath = get_setting(App, str(1) if App == "R64" else str(0))
        ahk_path = os.path.join(sublime.packages_path(), 'Enhanced-R', 'bin','AutoHotkey')
        ahk_script_path = os.path.join(sublime.packages_path(), 'Enhanced-R', 'bin','Rgui.ahk')
        # manually add "\n" to keep the indentation of first line of block code,
        # "\n" is later removed in AutoHotkey script
        cmd = "\n"+cmd

        args = [ahk_path, ahk_script_path, progpath, cmd ]
        subprocess.Popen(args)

    elif plat == 'linux':
        App = get_setting("App", "tmux")
        if App == "tmux":
            progpath = get_setting("tmux", "tmux")
            subprocess.call([progpath, 'set-buffer', cmd + "\n"])
            subprocess.call([progpath, 'paste-buffer', '-d'])

        elif App == "screen":
            progpath = get_setting("screen", "screen")
            subprocess.call([progpath, '-X', 'stuff', cmd + "\n"])


class RSendSelectCommand(sublime_plugin.TextCommand):

    # expand selection to {...} when being triggered
    def expand_sel(self, sel):
        esel = self.view.find(r"""^.*(\{(?:(["\'])(?:[^\\]|\\.)*?\2|#.*$|[^\{\}]|(?1))*\})"""
            , self.view.line(sel).begin())
        if self.view.line(sel).begin() == esel.begin():
            return esel

    def run(self, edit):
        cmd = ''
        for sel in self.view.sel():
            if sel.empty():
                thiscmd = self.view.substr(self.view.line(sel))
                # if the line ends with {, expand to {...}
                if re.match(r".*\{\s*$", thiscmd):
                    esel = self.expand_sel(sel)
                    if esel:
                        thiscmd = self.view.substr(esel)
            else:
                thiscmd = self.view.substr(sel)
            cmd += thiscmd +'\n'
        rcmd(cmd)

class RChangeDirCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        fname = self.view.file_name()
        if not fname:
            sublime.error_message("Save the file!")
            return
        dirname = os.path.dirname(fname)
        cmd = "setwd(\"" + escape_dq(dirname) + "\")"
        rcmd(cmd)

class RSourceCodeCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        fname = self.view.file_name()
        if not fname:
            sublime.error_message("Save the file!")
            return
        cmd = "source(\"" +  escape_dq(fname) + "\")"
        rcmd(cmd)

class RappSwitcher(sublime_plugin.WindowCommand):

    def show_quick_panel(self, options, done):
        sublime.set_timeout(lambda: self.window.show_quick_panel(options, done), 10)

    def run(self):
        plat = sublime.platform()
        if plat == 'osx':
            self.app_list = ["R", "R64", "Terminal", "iTerm"]
            pop_string = ["R is 64 bit for 3.x.x", "R 2.x.x only", "Terminal", "iTerm 2"]
        elif plat == "windows":
            self.app_list = ["R32", "R64"]
            pop_string = ["R i386", "R x64"]
        elif plat == "linux":
            self.app_list = ["tmux", "screen"]
            pop_string = ["tmux", "screen"]
        else:
            sublime.error_message("Platform not supported!")

        self.show_quick_panel([list(z) for z in zip(self.app_list, pop_string)], self.on_done)

    def on_done(self, action):
        if action==-1: return
        settings = sublime.load_settings(settingsfile)
        plat = sublime.platform()
        if plat == 'osx':
            plat_settings = settings.get('osx')
            plat_settings['App'] = self.app_list[action]
            settings.set('osx', plat_settings)
        elif plat == "windows":
            plat_settings = settings.get('windows')
            plat_settings['App'] = self.app_list[action]
            settings.set('windows', plat_settings)
        elif plat == "linux":
            plat_settings = settings.get('linux')
            plat_settings['App'] = self.app_list[action]
            settings.set('linux', plat_settings)

        sublime.save_settings(settingsfile)
