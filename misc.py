import sublime, sublime_plugin
import os
import re
import sys

# escape double quote
def escape_dq(string):
    string = string.replace('\\', '\\\\')
    string = string.replace('"', '\\"')
    return string

# get setting key
def RBoxSettings(key, default=None):
    plat = sublime.platform()
    settings = sublime.load_settings('R-Box.sublime-settings')
    return settings.get(key, default)

# List a directory using quick panel
def listdir(view, dir, base, ext, on_done):
    if not os.path.isdir(dir):
        sublime.status_message("Directory %s does not exist." % dir)
        return
    ls = os.listdir(dir)
    if ext:
        fnames = [f for f in ls if os.path.splitext(f)[1].lower() in ext]
    else:
        fnames = [f for f in ls if os.path.isfile(os.path.join(dir, f))]
    if base:
        fnames = [f for f in fnames if base.lower() in f.lower()]

    display = [os.curdir, os.pardir]+ [">"+f for f in ls if os.path.isdir(os.path.join(dir, f))] + fnames

    def on_action(i):
        if i<0: return
        elif i<1 or display[i][0] == '>':
            target = display[i][2:] if display[i][0] == '>' else display[i]
            target_dir = os.path.normpath(os.path.join(dir, target))
            sublime.set_timeout(lambda: listdir(view, target_dir, base, ext, on_done), 1)
        else:
            target_dir = os.path.normpath(os.path.join(dir, display[i]))
            on_done(target_dir)

    sublime.set_timeout(lambda: view.window().show_quick_panel(display, on_action), 1)
