import sublime
import sublime_plugin
import os
import subprocess
import re
import sys


class SendTextMixin:

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
        args.extend(['-e', 'tell app "Terminal" to do script "' + cmd + '" in front window'])
        subprocess.Popen(args)

    def _send_text_iterm(self, cmd):
        cmd = self.clean_cmd(cmd)
        cmd = self.escape_dquote(cmd)
        ver = self.iterm_version()
        if ver >= (2, 9):
            args = ['osascript', '-e', 'tell app "iTerm" to tell the first window ' +
                    'to tell current session to write text "' + cmd + '"']
        else:
            args = ['osascript', '-e', 'tell app "iTerm" to tell the first terminal ' +
                    'to tell current session to write text "' + cmd + '"']
        subprocess.check_call(args)

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
        ahk_path = os.path.join(sublime.packages_path(), 'User', 'R-Box', 'bin', 'AutoHotkeyU32')
        ahk_script_path = os.path.join(sublime.packages_path(), 'User', 'R-Box', 'bin', script)
        # manually add "\n" to keep the indentation of first line of block code,
        # "\n" is later removed in AutoHotkey script
        cmd = "\n" + cmd
        args = [ahk_path, ahk_script_path, progpath, cmd]
        subprocess.Popen(args)

    def send_text(self, cmd):
        view = self.view
        if cmd.strip() == "":
            return
        plat = sublime.platform()
        settings = sublime.load_settings('R-Box.sublime-settings')
        if plat == "osx":
            prog = settings.get("prog", "R")
        if plat == "windows":
            prog = settings.get("prog", "R64")
        if plat == "linux":
            prog = settings.get("prog", "tmux")

        if prog == 'Terminal':
            self._send_text_terminal(cmd)

        elif prog == 'iTerm':
            self._send_text_iterm(cmd)

        elif plat == "osx" and re.match('R[0-9]*$', prog):
            cmd = self.clean_cmd(cmd)
            cmd = self.escape_dquote(cmd)
            args = ['osascript']
            args.extend(['-e', 'tell app "' + prog + '" to cmd "' + cmd + '"'])
            subprocess.Popen(args)

        elif prog == "tmux":
            self._send_text_tmux(cmd, settings.get("tmux", "tmux"))

        elif prog == "screen":
            self._send_text_screen(cmd, settings.get("screen", "screen"))

        elif prog == "SublimeREPL":
            cmd = self.clean_cmd(cmd)
            external_id = view.scope_name(0).split(" ")[0].split(".", 1)[1]
            sublime.active_window().run_command(
                "repl_send", {"external_id": external_id, "text": cmd})
            return

        elif plat == "windows" and re.match('R[0-9]*$', prog):
            progpath = settings.get(prog, "1" if prog == "R64" else "0")
            self._send_text_ahk(cmd, progpath, "Rgui.ahk")

        elif prog == "Cygwin":
            self._send_text_ahk(cmd, "", "Cygwin.ahk")

        elif prog == "Cmder":
            self._send_text_ahk(cmd, "", "Cmder.ahk")


class ExpandBlockMixin:

    def expand_block(self, sel):
        # expand selection to {...}
        view = self.view
        thiscmd = view.substr(view.line(sel))
        if re.match(r".*\{\s*$", thiscmd):
            esel = view.find(
                r"""^(?:.*(\{(?:(["\'])(?:[^\\]|\\.)*?\2|#.*$|[^\{\}]|(?1))*\})[^\{\}\n]*)+""",
                view.line(sel).begin()
            )
            if view.line(sel).begin() == esel.begin():
                sel = esel
        return sel


class RBoxSendSelectionCommand(sublime_plugin.TextCommand, SendTextMixin, ExpandBlockMixin):
    def run(self, edit):
        view = self.view
        settings = sublime.load_settings('R-Box.sublime-settings')
        cmd = ''
        moved = False
        for sel in [s for s in view.sel()]:
            if sel.empty():
                esel = self.expand_block(sel)
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

        self.send_text(cmd)

        if moved:
            view.show(view.sel())


class RBoxChangeDirCommand(sublime_plugin.TextCommand, SendTextMixin):
    def run(self, edit):
        view = self.view
        fname = view.file_name()
        if not fname:
            sublime.error_message("Save the file!")
            return
        dirname = os.path.dirname(fname)
        cmd = "setwd(\"" + self.escape_dquote(dirname) + "\")"
        self.send_text(cmd)


class RBoxSourceCodeCommand(sublime_plugin.TextCommand, SendTextMixin):
    def run(self, edit):
        view = self.view
        fname = view.file_name()
        if not fname:
            sublime.error_message("Save the file!")
            return
        cmd = "source(\"" + self.escape_dquote(fname) + "\")"
        self.send_text(cmd)


class RBoxBuildCommand(sublime_plugin.WindowCommand):

    def run(self):
        self.window.active_view().run_command("r_box_source_code")


# old send text class of Enhanced-R
class RSendSelectCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        self.run_command("r_box_send_selection")


class RBoxChooseProgramCommand(sublime_plugin.WindowCommand):

    def show_quick_panel(self, options, done):
        sublime.set_timeout(lambda: self.window.show_quick_panel(options, done), 10)

    def run(self):
        plat = sublime.platform()
        if plat == 'osx':
            self.app_list = ["R", "Terminal", "iTerm", "tmux", "screen", "SublimeREPL"]
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
