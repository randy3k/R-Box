import sublime


def plugin_loaded():
    s = sublime.load_settings("SublimeLinter.sublime-settings")
    if s.has("user"):
        user = s.get("user")
        syntax_map = user.get("syntax_map", {})
        if "r extended" not in syntax_map:
            syntax_map.update({"r extended": "r"})
            user["syntax_map"] = syntax_map
            s.set("user", user)
            sublime.save_settings("SublimeLinter.sublime-settings")
