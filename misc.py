import sublime, sublime_plugin
import os
import re
import sys

# get setting key
def RBoxSettings(key, default=None):
    plat = sublime.platform()
    settings = sublime.load_settings('R-Box.sublime-settings')
    return settings.get(key, default)

if sys.platform == "win32":
    def update_resource(binname):
        # from https://github.com/weslly/ColorPicker/blob/master/sublimecp.py=
        targetdir = os.path.join(sublime.packages_path(), 'User', 'R-Box', 'bin')
        targetpath = os.path.join(targetdir, binname)
        respath = 'Packages/R-Box/bin/' + binname
        pkgpath = os.path.join(sublime.installed_packages_path(), 'R-Box.sublime-package')
        unpkgpath = os.path.join(sublime.packages_path(), 'R-Box', 'bin', binname)

        if os.path.exists(targetpath):
            targetinfo = os.stat(targetpath)
        else:
            if not os.path.exists(targetdir):
                os.makedirs(targetdir, 0o755)
            targetinfo = None

        if os.path.exists(unpkgpath):
            pkginfo = os.stat(unpkgpath)
        elif os.path.exists(pkgpath):
            pkginfo = os.stat(pkgpath)
        else:
            return

        if targetinfo == None or targetinfo.st_mtime < pkginfo.st_mtime:
            data = sublime.load_binary_resource(respath)
            print("* Updating " + targetpath)
            with open(targetpath, 'wb') as binfile:
                binfile.write(data)
                binfile.close()

        if not os.access(targetpath, os.X_OK):
            os.chmod(targetpath, 0o755)

    def plugin_loaded():
        update_resource("AutoHotkeyU32.exe")
        update_resource("Rgui.ahk")
