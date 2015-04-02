import sublime


def plugin_loaded():
    settings_file = 'R-Box.sublime-settings'
    settings = sublime.load_settings(settings_file)
    if settings.has("App"):
        settings.set('prog', settings.get("App"))
        settings.erase("App")
        sublime.save_settings(settings_file)

if sublime.version() < '3000':
    plugin_loaded()
