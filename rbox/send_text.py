import sublime
import sublime_plugin
import os
import subprocess
import re


def sget(key, default=None):
    s = sublime.load_settings("R-Box.sublime-settings")
    return s.get(key, default)


class TextSender:

    def __init__(self):
        plat = sublime.platform()
        defaults = {"osx": "R", "windows": "R64", "linux": "tmux"}
        prog = sget("prog", defaults[plat])
        function_str = "_dispatch_" + prog.lower().replace("-", "_")
        if getattr(self, function_str + "_" + plat, None):
            function_str = function_str + "_" + plat
        self.send_text = eval("self." + function_str)

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

    def _dispatch_terminal(self, cmd):
        cmd = self.clean_cmd(cmd)
        cmd = self.escape_dquote(cmd)
        args = ['osascript']
        args.extend(['-e',
                     'tell application "Terminal" to do script "' + cmd + '" in front window'])
        subprocess.Popen(args)

    @staticmethod
    def iterm_version():
        args = ['osascript', '-e', 'tell application "iTerm" to get version']
        ver = subprocess.check_output(args).decode().strip()
        return tuple((int(i) for i in re.split(r"\.", ver)[0:2]))

    def _dispatch_iterm(self, cmd):
        cmd = self.clean_cmd(cmd)
        if self.iterm_version() >= (2, 9):
            n = 1000
            chunks = [cmd[i:i+n] for i in range(0, len(cmd), n)]
            for chunk in chunks:
                subprocess.call([
                    'osascript', '-e',
                    'tell application "iTerm" to tell the current window ' +
                    'to tell current session to write text "' +
                    self.escape_dquote(chunk) + '" without newline'
                ])
            subprocess.call([
                'osascript', '-e',
                'tell application "iTerm" to tell the current window ' +
                'to tell current session to write text ""'
            ])
        else:
            subprocess.call([
                'osascript', '-e',
                'tell application "iTerm" to tell the current terminal ' +
                'to tell current session to write text "' +
                self.escape_dquote(cmd) + '"'
            ])

    def _dispatch_r_osx(self, cmd):
        cmd = self.clean_cmd(cmd)
        cmd = self.escape_dquote(cmd)
        args = ['osascript']
        args.extend(['-e', 'tell application "R" to cmd "' + cmd + '"'])
        subprocess.Popen(args)

    def _dispatch_rstudio_osx(self, cmd):
        cmd = self.clean_cmd(cmd)
        script = """
        on run argv
            tell application "RStudio"
                cmd item 1 of argv
            end tell
        end run
        """
        subprocess.call(['osascript', '-e', script, cmd])

    def _dispatch_tmux(self, cmd):
        tmux = sget("tmux", "tmux")
        cmd = self.clean_cmd(cmd) + "\n"
        n = 200
        chunks = [cmd[i:i+n] for i in range(0, len(cmd), n)]
        for chunk in chunks:
            subprocess.call([tmux, 'set-buffer', chunk])
            subprocess.call([tmux, 'paste-buffer', '-d'])

    def _dispatch_screen(self, cmd):
        screen = sget("screen", "screen")
        plat = sublime.platform()
        cmd = self.clean_cmd(cmd) + "\n"
        n = 200
        chunks = [cmd[i:i+n] for i in range(0, len(cmd), n)]
        for chunk in chunks:
            if plat == "linux":
                chunk = chunk.replace("\\", r"\\")
                chunk = chunk.replace("$", r"\$")
            subprocess.call([screen, '-X', 'stuff', chunk])

    @staticmethod
    def execute_ahk_script(script, cmd, args=[]):
        ahk_path = os.path.join(sublime.packages_path(),
                                'User', 'R-Box', 'bin', 'AutoHotkeyU32')
        ahk_script_path = os.path.join(sublime.packages_path(),
                                       'User', 'R-Box', 'bin', script)
        # manually add "\n" to keep the indentation of first line of block code,
        # "\n" is later removed in AutoHotkey script
        cmd = "\n" + cmd
        subprocess.Popen([ahk_path, ahk_script_path, cmd] + args)

    def _dispatch_r32_windows(self, cmd):
        cmd = self.clean_cmd(cmd)
        self.execute_ahk_script("Rgui.ahk", cmd, [sget("R32", "0")])

    def _dispatch_r64_windows(self, cmd):
        cmd = self.clean_cmd(cmd)
        self.execute_ahk_script("Rgui.ahk", cmd, [sget("R64", "1")])

    def _dispatch_rstudio_windows(self, cmd):
        cmd = self.clean_cmd(cmd)
        self.execute_ahk_script("RStudio.ahk", cmd)

    def _dispatch_cygwin(self, cmd):
        cmd = self.clean_cmd(cmd)
        self.execute_ahk_script("Cygwin.ahk", cmd)

    def _dispatch_cmder(self, cmd):
        cmd = self.clean_cmd(cmd)
        self.execute_ahk_script("Cmder.ahk", cmd)

    def _dispatch_sublimerepl(self, cmd):
        cmd = self.clean_cmd(cmd)
        window = sublime.active_window()
        view = window.active_view()
        external_id = view.scope_name(0).split(" ")[0].split(".", 1)[1]
        window.run_command(
            "repl_send", {"external_id": external_id, "text": cmd})


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
        if sget("auto_advance_non_empty", True):
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
            self.app_list = ["R", "RStudio", "Terminal", "iTerm", "tmux", "screen", "SublimeREPL"]
        elif plat == "windows":
            self.app_list = ["R32", "R64", "RStudio", "Cmder", "Cygwin", "SublimeREPL"]
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
