import sublime

# get setting key
def RBoxSettings(key, default=None):
    plat = sublime.platform()
    settings = sublime.load_settings('R-Box.sublime-settings')
    return settings.get(key, default)