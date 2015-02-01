import sublime
import sublime_plugin
import os
import subprocess
import re
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


def iTerm_version():
    try:
        args = ['osascript', '-e',
                'tell app "iTerm" to tell the first terminal to set foo to true']
        subprocess.Popen(args)
        return 2.9
    except:
        return 2.0


def sendtext(cmd):
    if cmd.strip() == "":
        return
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
        cmd = cmd.split("\n")
        line_len = [len(c) for c in cmd]
        k = 0
        ver = iTerm_version()
        while k < len(line_len):
            for j in range(k + 1, len(line_len) + 1):
                if sum(line_len[k:(j+1)]) > 1000:
                    break
            chunk = "\n".join(cmd[k:j])
            if ver == 2.0:
                args = ['osascript', '-e', 'tell app "iTerm" to tell the first terminal '
                        'to tell current session to write text "' + chunk + '"']
            else:
                args = ['osascript', '-e', 'tell app "iTerm" to tell the first terminal window '
                        'to tell current session to write text "' + chunk + '"']

            # when chunk ends in a space, iterm does not execute.
            if (chunk[-1:] == ' '):
                if ver == 2.0:
                    args += ['-e', 'tell app "iTerm" to tell the first terminal '
                             'to tell current session to write text ""']
                else:
                    args += ['-e', 'tell app "iTerm" to tell the first terminal window '
                             'to tell current session to write text ""']

            subprocess.check_call(args)

            k = j

    elif plat == "osx" and re.match('R[0-9]*$', prog):
        cmd = clean(cmd)
        cmd = escape_dq(cmd)
        args = ['osascript']
        args.extend(['-e', 'tell app "' + prog + '" to cmd "' + cmd + '"'])
        subprocess.Popen(args)

    elif prog == "tmux":
        cmd = clean(cmd) + "\n"
        progpath = RBoxSettings("tmux", "tmux")
        n = 200
        chunks = [cmd[i:i+n] for i in range(0, len(cmd), n)]
        for chunk in chunks:
            subprocess.call([progpath, 'set-buffer', chunk])
            subprocess.call([progpath, 'paste-buffer', '-d'])

    elif prog == "screen":
        cmd = clean(cmd) + "\n"
        progpath = RBoxSettings("screen", "screen")
        n = 200
        chunks = [cmd[i:i+n] for i in range(0, len(cmd), n)]
        for chunk in chunks:
            if plat == "linux":
                chunk = chunk.replace("\\", r"\\")
                chunk = chunk.replace("$", r"\$")
            subprocess.call([progpath, '-X', 'stuff', chunk])

    elif prog == "SublimeREPL":
        cmd = clean(cmd)
        view = sublime.active_window().active_view()
        external_id = view.scope_name(0).split(" ")[0].split(".", 1)[1]
        sublime.active_window().run_command("repl_send", {"external_id": external_id, "text": cmd})
        return

    elif plat == "windows" and re.match('R[0-9]*$', prog):
        cmd = clean(cmd)
        progpath = RBoxSettings(prog, str(1) if prog == "R64" else str(0))
        ahk_path = os.path.join(sublime.packages_path(), 'User', 'R-Box', 'bin', 'AutoHotkeyU32')
        ahk_script_path = os.path.join(sublime.packages_path(), 'User', 'R-Box', 'bin', 'Rgui.ahk')
        # manually add "\n" to keep the indentation of first line of block code,
        # "\n" is later removed in AutoHotkey script
        cmd = "\n"+cmd
        args = [ahk_path, ahk_script_path, progpath, cmd]
        subprocess.Popen(args)


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
        cmd = ''
        moved = False
        for sel in [s for s in view.sel()]:
            if sel.empty():
                esel = expand_block(view, sel)
                thiscmd = view.substr(view.line(esel))
                line = view.rowcol(esel.end())[0]
                if RBoxSettings("auto_advance", False):
                    view.sel().subtract(sel)
                    pt = view.text_point(line+1, 0)
                    view.sel().add(sublime.Region(pt, pt))
                    moved = True
            else:
                thiscmd = view.substr(sel)
            cmd += thiscmd + '\n'

        sendtext(cmd)

        if moved:
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
        cmd = "source(\"" + escape_dq(fname) + "\")"
        sendtext(cmd)
