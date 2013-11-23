import sublime
import sublime_plugin

settingsfile = 'Enhanced-R.sublime-settings'

class RappSwitch(sublime_plugin.WindowCommand):

    def show_quick_panel(self, options, done):
        sublime.set_timeout(lambda: self.window.show_quick_panel(options, done), 10)

    def run(self):
        plat = sublime.platform()
        if plat == 'osx':
            self.app_list = ["R", "R64", "Terminal", "iTerm", "SublimeREPL", "RStudio"]
            pop_string = ["R is 64 bit for 3.x.x", "R 2.x.x only", "Terminal", "iTerm 2", "SublimeREPL", "RStudio"]
        elif plat == "windows":
            self.app_list = ["R32", "R64", "SublimeREPL"]
            pop_string = ["R i386", "R x64", "SublimeREPL"]
        elif plat == "linux":
            self.app_list = ["tmux", "screen", "SublimeREPL"]
            pop_string = ["tmux", "screen", "SublimeREPL"]
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
