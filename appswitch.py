import sublime
import sublime_plugin


class RBoxAppSwitch(sublime_plugin.WindowCommand):

    def show_quick_panel(self, options, done):
        sublime.set_timeout(lambda: self.window.show_quick_panel(options, done), 10)

    def run(self):
        plat = sublime.platform()
        if plat == 'osx':
            self.app_list = ["R", "Terminal", "iTerm", "tmux", "screen", "SublimeREPL"]
            pop_string = ["", "Terminal", "iTerm 2", "tmux", "screen", "SublimeREPL"]
        elif plat == "windows":
            self.app_list = ["R32", "R64", "Cmder", "Cygwin", "SublimeREPL"]
            pop_string = ["R i386", "R x64", "Cmder", "Cygwin", "SublimeREPL"]
        elif plat == "linux":
            self.app_list = ["tmux", "screen", "SublimeREPL"]
            pop_string = ["tmux", "screen", "SublimeREPL"]
        else:
            sublime.error_message("Platform not supported!")

        self.show_quick_panel([list(z) for z in zip(self.app_list, pop_string)], self.on_done)

    def on_done(self, action):
        if action == -1:
            return
        settings = sublime.load_settings('R-Box.sublime-settings')
        settings.set('App', self.app_list[action])
        sublime.save_settings('R-Box.sublime-settings')
