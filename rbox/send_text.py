import sublime
import sublime_plugin
import os
import subprocess
import re
import sys


def sget(key, default=None):
    s = sublime.load_settings("R-Box.sublime-settings")
    return s.get(key, default)


class TextSender:

    @staticmethod
    def clean_cmd(cmd):
        cmd = cmd.expandtabs(4)
        cmd = cmd.rstrip('\n')
        if len(re.findall("\n", cmd)) == 0:
            cmd = cmd.lstrip()
        return cmd

    @staticmethod
    def escape_dquote(cmd):
        cmd = cmd.replace('\\', '\\\\')
        cmd = cmd.replace('"', '\\"')
        return cmd

    @staticmethod
    def iterm_version():
        args = ['osascript', '-e', 'tell application "iTerm" to get version']
        ver = subprocess.check_output(args).decode().strip()
        return tuple((int(i) for i in re.split(r"\.", ver)[0:2]))

    def _send_text_terminal(self, cmd):
        cmd = self.clean_cmd(cmd)
        cmd = self.escape_dquote(cmd)
        args = ['osascript']
        args.extend(['-e',
                     'tell application "Terminal" to do script "' + cmd + '" in front window'])
        subprocess.Popen(args)

    def _send_text_iterm(self, cmd):
        cmd = self.clean_cmd(cmd)
        if self.iterm_version() >= (2, 9):
            cmd = cmd
            n = 1000
            chunks = [cmd[i:i+n] for i in range(0, len(cmd), n)]
            for chunk in chunks:
                subprocess.call([
                    'osascript', '-e',
                    'tell application "iTerm" to tell the first window ' +
                    'to tell current session to write text "' +
                    self.escape_dquote(chunk) + '" without newline'
                ])
            subprocess.call([
                'osascript', '-e',
                'tell application "iTerm" to tell the first window ' +
                'to tell current session to write text ""'
            ])
        else:
            subprocess.call([
                'osascript', '-e',
                'tell application "iTerm" to tell the first terminal ' +
                'to tell current session to write text "' +
                self.escape_dquote(cmd) + '"'
            ])

    def _send_text_tmux(self, cmd, tmux="tmux"):
        cmd = self.clean_cmd(cmd) + "\n"
        n = 200
        chunks = [cmd[i:i+n] for i in range(0, len(cmd), n)]
        for chunk in chunks:
            subprocess.call([tmux, 'set-buffer', chunk])
            subprocess.call([tmux, 'paste-buffer', '-d'])

    def _send_text_screen(self, cmd, screen="screen"):
        plat = sys.platform
        cmd = self.clean_cmd(cmd) + "\n"
        n = 200
        chunks = [cmd[i:i+n] for i in range(0, len(cmd), n)]
        for chunk in chunks:
            if plat.startswith("linux"):
                chunk = chunk.replace("\\", r"\\")
                chunk = chunk.replace("$", r"\$")
            subprocess.call([screen, '-X', 'stuff', chunk])

    def _send_text_ahk(self, cmd, progpath="", script="Rgui.ahk"):
        cmd = self.clean_cmd(cmd)
        ahk_path = os.path.join(sublime.packages_path(),
                                'User', 'R-Box', 'bin', 'AutoHotkeyU32')
        ahk_script_path = os.path.join(sublime.packages_path(),
                                       'User', 'R-Box', 'bin', script)
        # manually add "\n" to keep the indentation of first line of block code,
        # "\n" is later removed in AutoHotkey script
        cmd = "\n" + cmd
        subprocess.Popen([ahk_path, ahk_script_path, progpath, cmd])

    def _send_text_r_ide(self, cmd, prog):
        cmd = self.clean_cmd(cmd)
        cmd = self.escape_dquote(cmd)
        args = ['osascript']
        args.extend(['-e', 'tell application "' + prog + '" to cmd "' + cmd + '"'])
        subprocess.Popen(args)

    def _send_text_sublime_repl(self, cmd):
        cmd = self.clean_cmd(cmd)
        window = sublime.active_window()
        view = window.active_view()
        external_id = view.scope_name(0).split(" ")[0].split(".", 1)[1]
        window.run_command(
            "repl_send", {"external_id": external_id, "text": cmd})

    def send_text(self, cmd):
        plat = sublime.platform()
        if plat == "osx":
            prog = sget("prog", "R")
        if plat == "windows":
            prog = sget("prog", "R64")
        if plat == "linux":
            prog = sget("prog", "tmux")

        if prog == 'Terminal':
            self._send_text_terminal(cmd)

        elif prog == 'iTerm':
            self._send_text_iterm(cmd)

        elif prog == "tmux":
            self._send_text_tmux(cmd, sget("tmux", "tmux"))

        elif prog == "screen":
            self._send_text_screen(cmd, sget("screen", "screen"))

        elif prog == "SublimeREPL":
            self._send_text_sublime_repl(cmd)

        elif prog == "Cygwin":
            self._send_text_ahk(cmd, "", "Cygwin.ahk")

        elif prog == "Cmder":
            self._send_text_ahk(cmd, "", "Cmder.ahk")

        elif plat == "osx" and re.match('(R[0-9]*|RStudio)$', prog):
            self._send_text_r_ide(cmd, prog)

        elif plat == "windows" and re.match('R[0-9]*$', prog):
            progpath = sget(prog, "1" if prog == "R64" else "0")
            self._send_text_ahk(cmd, progpath, "Rgui.ahk")


class TextGetter:

    def __init__(self, view):
        self.view = view

    def expand_line(self, s):
        view = self.view
        # expand selection to {...}
        s = view.line(s)
        thiscmd = view.substr(s)
        if re.match(r".*\{\s*$", thiscmd):
            es = view.find(
                r"""^(?:.*(\{(?:(["\'])(?:[^\\]|\\.)*?\2|#.*$|[^\{\}]|(?1))*\})[^\{\}\n]*)+""",
                view.line(s).begin()
            )
            if s.begin() == es.begin():
                s = es
        return s

    def advance(self, s):
        view = self.view
        view.sel().subtract(s)
        pt = view.text_point(view.rowcol(s.end())[0]+1, 0)
        nextpt = view.find(r"\S", pt)
        if nextpt.begin() != -1:
            pt = view.text_point(view.rowcol(nextpt.begin())[0], 0)
        view.sel().add(sublime.Region(pt, pt))

    def get_text(self):
        view = self.view
        cmd = ''
        moved = False
        for s in [s for s in view.sel()]:
            if s.empty():
                s = self.expand_line(s)
                if sget("auto_advance", True):
                    self.advance(s)
                    moved = True

            cmd += view.substr(s) + '\n'

        if moved:
            view.show(view.sel())

        return cmd


class RBoxSendSelectionCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        view = self.view
        getter = TextGetter(view)
        cmd = getter.get_text()
        sender = TextSender()
        sender.send_text(cmd)


class RBoxChangeDirCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        view = self.view
        fname = view.file_name()
        if not fname:
            sublime.error_message("Save the file!")
            return
        dirname = os.path.dirname(fname)
        sender = TextSender()
        cmd = "setwd(\"" + sender.escape_dquote(dirname) + "\")"
        sender.send_text(cmd)


class RBoxSourceCodeCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        view = self.view
        fname = view.file_name()
        if not fname:
            sublime.error_message("Save the file!")
            return
        sender = TextSender()
        cmd = "source(\"" + sender.escape_dquote(fname) + "\")"
        sender.send_text(cmd)


class RBoxBuildCommand(sublime_plugin.WindowCommand):

    def run(self):
        self.window.active_view().run_command("r_box_source_code")


class RBoxChooseProgramCommand(sublime_plugin.WindowCommand):

    def show_quick_panel(self, options, done):
        sublime.set_timeout(lambda: self.window.show_quick_panel(options, done), 10)

    def run(self):
        plat = sublime.platform()
        if plat == 'osx':
            self.app_list = ["R", "Terminal", "iTerm", "tmux", "screen", "RStudio", "SublimeREPL"]
        elif plat == "windows":
            self.app_list = ["R32", "R64", "Cmder", "Cygwin", "SublimeREPL"]
        elif plat == "linux":
            self.app_list = ["tmux", "screen", "SublimeREPL"]
        else:
            sublime.error_message("Platform not supported!")

        self.show_quick_panel(self.app_list, self.on_done)

    def on_done(self, action):
        if action == -1:
            return
        settings = sublime.load_settings('R-Box.sublime-settings')
        settings.set("prog", self.app_list[action])
        sublime.save_settings('R-Box.sublime-settings')
