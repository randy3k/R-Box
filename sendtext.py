import sublime
import sublime_plugin
import os
import subprocess
import re
import time
import sys
import tempfile
from .misc import RBoxSettings

def clean(cmd):
    cmd = cmd.expandtabs(4)
    cmd = cmd.rstrip('\n')
    if len(re.findall("\n", cmd)) == 0:
        cmd = cmd.lstrip()
    return cmd

def escape_dq(cmd):
    cmd = cmd.replace('\\', '\\\\')
    cmd = cmd.replace('"', '\\"')
    return cmd

def sendtext(cmd):
    plat = sublime.platform()
    if plat == "osx":
        prog = RBoxSettings("App", "R")
    if plat == "windows":
        prog = RBoxSettings("App", "R64")
    if plat == "linux":
        prog = RBoxSettings("App", "tmux")

    if re.match('Terminal', prog):
        cmd = clean(cmd)
        cmd = escape_dq(cmd)
        args = ['osascript']
        args.extend(['-e', 'tell app "Terminal" to do script "' + cmd + '" in front window\n'])
        subprocess.Popen(args)

    elif re.match('iTerm', prog):
        cmd = clean(cmd)
        cmd = escape_dq(cmd)
        # when cmd ends in a space, iterm does not execute. Thus append a line break.
        if (cmd[-1:] == ' '):
            cmd += '\n'
        args = ['osascript']
        args.extend(['-e', 'tell app "iTerm" to tell the first terminal to tell current session to write text "' + cmd +'"'])
        subprocess.Popen(args)

    elif plat == "osx" and re.match('R[0-9]*$', prog):
        cmd = clean(cmd)
        cmd = escape_dq(cmd)
        args = ['osascript']
        args.extend(['-e', 'tell app "' + prog + '" to cmd "' + cmd + '"'])
        subprocess.Popen(args)

    elif plat == "windows" and re.match('R[0-9]*$', prog):
        progpath = RBoxSettings(prog, str(1) if prog == "R64" else str(0))
        ahk_path = os.path.join(sublime.packages_path(), 'User', 'R-Box', 'bin','AutoHotkeyU32')
        ahk_script_path = os.path.join(sublime.packages_path(), 'User', 'R-Box', 'bin','Rgui.ahk')
        # manually add "\n" to keep the indentation of first line of block code,
        # "\n" is later removed in AutoHotkey script
        cmd = "\n"+cmd
        args = [ahk_path, ahk_script_path, progpath, cmd ]
        subprocess.Popen(args)

    elif prog == "tmux":
        progpath = RBoxSettings("tmux", "tmux")
        subprocess.call([progpath, 'set-buffer', cmd + "\n"])
        subprocess.call([progpath, 'paste-buffer', '-d'])

    elif prog == "screen":
        progpath = RBoxSettings("screen", "screen")
        if len(cmd)<2000:
            subprocess.call([progpath, '-X', 'stuff', cmd])
        else:
            with tempfile.NamedTemporaryFile() as tmp:
                with open(tmp.name, 'w') as f:
                    f.write(cmd)
                    subprocess.call([progpath, '-X', 'stuff', ". %s\n" % (f.name)])

    elif prog == "SublimeREPL":
            external_id = self.view.scope_name(0).split(" ")[0].split(".", 1)[1]
            self.view.window().run_command("repl_send", {"external_id": external_id, "text": cmd})
            return

class RBoxSendSelectionCommand(sublime_plugin.TextCommand):

    # expand selection to {...} when being triggered
    def expand_sel(self, sel):
        esel = self.view.find(r"""^(?:.*(\{(?:(["\'])(?:[^\\]|\\.)*?\2|#.*$|[^\{\}]|(?1))*\})[^\{\}\n]*)+"""
            , self.view.line(sel).begin())
        if self.view.line(sel).begin() == esel.begin():
            return esel

    def run(self, edit):
        view = self.view
        cmd = ''
        for sel in [s for s in view.sel()]:
            if sel.empty():
                thiscmd = view.substr(view.line(sel))
                line = view.rowcol(sel.end())[0]
                # if the line ends with {, expand to {...}
                if re.match(r".*\{\s*$", thiscmd):
                    esel = self.expand_sel(sel)
                    if esel:
                        thiscmd = view.substr(esel)
                        line = view.rowcol(esel.end())[0]
                if RBoxSettings("auto_advance", False):
                    view.sel().subtract(sel)
                    pt = view.text_point(line+1,0)
                    view.sel().add(sublime.Region(pt,pt))
            else:
                thiscmd = view.substr(sel)
            cmd += thiscmd +'\n'

        sendtext(cmd)

        if RBoxSettings("auto_advance", False):
            view.show(view.sel())

class RBoxChangeDirCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        fname = self.view.file_name()
        if not fname:
            sublime.error_message("Save the file!")
            return
        dirname = os.path.dirname(fname)
        cmd = "setwd(\"" + escape_dq(dirname) + "\")"
        sendtext(cmd)

class RBoxSourceCodeCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        fname = self.view.file_name()
        if not fname:
            sublime.error_message("Save the file!")
            return
        cmd = "source(\"" +  escape_dq(fname) + "\")"
        sendtext(cmd)
