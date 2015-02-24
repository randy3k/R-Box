import sublime
import sublime_plugin
import os
import subprocess
import re
import sys


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


def sendtext_terminal(cmd):
    cmd = clean(cmd)
    cmd = escape_dq(cmd)
    args = ['osascript']
    args.extend(['-e', 'tell app "Terminal" to do script "' + cmd + '" in front window'])
    subprocess.Popen(args)


def iterm_version():
    try:
        args = ['osascript', '-e',
                'tell app "iTerm" to tell the first terminal to set foo to true']
        subprocess.check_call(args)
        return 2.0
    except:
        return 2.9


def sendtext_iterm(cmd):
    cmd = clean(cmd)
    cmd = escape_dq(cmd)
    ver = iterm_version()
    if ver == 2.0:
        args = ['osascript', '-e', 'tell app "iTerm" to tell the first terminal ' +
                'to tell current session to write text "' + cmd + '"']
    else:
        args = ['osascript', '-e', 'tell app "iTerm" to tell the first terminal window ' +
                'to tell current session to write text "' + cmd + '"']
    subprocess.check_call(args)


def sendtext_tmux(cmd, tmux="tmux"):
    cmd = clean(cmd) + "\n"
    n = 200
    chunks = [cmd[i:i+n] for i in range(0, len(cmd), n)]
    for chunk in chunks:
        subprocess.call([tmux, 'set-buffer', chunk])
        subprocess.call([tmux, 'paste-buffer', '-d'])


def sendtext_screen(cmd, screen="screen"):
    plat = sys.platform
    cmd = clean(cmd) + "\n"
    n = 200
    chunks = [cmd[i:i+n] for i in range(0, len(cmd), n)]
    for chunk in chunks:
        if plat.startswith("linux"):
            chunk = chunk.replace("\\", r"\\")
            chunk = chunk.replace("$", r"\$")
        subprocess.call([screen, '-X', 'stuff', chunk])


def sendtext_ahk(cmd, progpath="", script="Rgui.ahk"):
    cmd = clean(cmd)
    ahk_path = os.path.join(sublime.packages_path(), 'User', 'R-Box', 'bin', 'AutoHotkeyU32')
    ahk_script_path = os.path.join(sublime.packages_path(), 'User', 'R-Box', 'bin', script)
    # manually add "\n" to keep the indentation of first line of block code,
    # "\n" is later removed in AutoHotkey script
    cmd = "\n"+cmd
    args = [ahk_path, ahk_script_path, progpath, cmd]
    subprocess.Popen(args)


def sendtext(view, cmd):
    if cmd.strip() == "":
        return
    plat = sublime.platform()
    settings = sublime.load_settings('R-Box.sublime-settings')
    if plat == "osx":
        prog = settings.get("App", "R")
    if plat == "windows":
        prog = settings.get("App", "R64")
    if plat == "linux":
        prog = settings.get("App", "tmux")

    if prog == 'Terminal':
        sendtext_terminal(cmd)

    elif prog == 'iTerm':
        sendtext_iterm(cmd)

    elif plat == "osx" and re.match('R[0-9]*$', prog):
        cmd = clean(cmd)
        cmd = escape_dq(cmd)
        args = ['osascript']
        args.extend(['-e', 'tell app "' + prog + '" to cmd "' + cmd + '"'])
        subprocess.Popen(args)

    elif prog == "tmux":
        sendtext_tmux(cmd, settings.get("tmux", "tmux"))

    elif prog == "screen":
        sendtext_screen(cmd, settings.get("screen", "screen"))

    elif prog == "SublimeREPL":
        cmd = clean(cmd)
        external_id = view.scope_name(0).split(" ")[0].split(".", 1)[1]
        sublime.active_window().run_command("repl_send", {"external_id": external_id, "text": cmd})
        return

    elif plat == "windows" and re.match('R[0-9]*$', prog):
        progpath = settings.get(prog, "1" if prog == "R64" else "0")
        sendtext_ahk(cmd, progpath, "Rgui.ahk")

    elif prog == "Cygwin":
        sendtext_ahk(cmd, "", "Cygwin.ahk")

    elif prog == "Cmder":
        sendtext_ahk(cmd, "", "Cmder.ahk")


def expand_block(view, sel):
    # expand selection to {...}
    thiscmd = view.substr(view.line(sel))
    if re.match(r".*\{\s*$", thiscmd):
        esel = view.find(
            r"""^(?:.*(\{(?:(["\'])(?:[^\\]|\\.)*?\2|#.*$|[^\{\}]|(?1))*\})[^\{\}\n]*)+""",
            view.line(sel).begin()
        )
        if view.line(sel).begin() == esel.begin():
            sel = esel
    return sel


class RBoxSendSelectionCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        view = self.view
        settings = sublime.load_settings('R-Box.sublime-settings')
        cmd = ''
        moved = False
        for sel in [s for s in view.sel()]:
            if sel.empty():
                esel = expand_block(view, sel)
                thiscmd = view.substr(view.line(esel))
                line = view.rowcol(esel.end())[0]
                if settings.get("auto_advance", False):
                    view.sel().subtract(sel)
                    pt = view.text_point(line+1, 0)
                    view.sel().add(sublime.Region(pt, pt))
                    moved = True
            else:
                thiscmd = view.substr(sel)
            cmd += thiscmd + '\n'

        sendtext(view, cmd)

        if moved:
            view.show(view.sel())


class RBoxChangeDirCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        view = self.view
        fname = view.file_name()
        if not fname:
            sublime.error_message("Save the file!")
            return
        dirname = os.path.dirname(fname)
        cmd = "setwd(\"" + escape_dq(dirname) + "\")"
        sendtext(view, cmd)


class RBoxSourceCodeCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        view = self.view
        fname = view.file_name()
        if not fname:
            sublime.error_message("Save the file!")
            return
        cmd = "source(\"" + escape_dq(fname) + "\")"
        sendtext(view, cmd)
