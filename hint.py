import sublime
import sublime_plugin
import os
import subprocess
import re
import sys
if sys.platform == "win32":
        from winreg import OpenKey, QueryValueEx, HKEY_LOCAL_MACHINE, KEY_READ
from .misc import *


def get_Rscript():
    plat = sublime.platform()
    if plat == "windows":
        arch = "x64" if RBoxSettings("App", "R64") == "R64" else "i386"
        Rscript = RBoxSettings("Rscript", None)
        if not Rscript:
            akey=OpenKey(HKEY_LOCAL_MACHINE, "SOFTWARE\\R-core\\R", 0, KEY_READ)
            path=QueryValueEx(akey, "InstallPath")[0]
            Rscript = path + "\\bin\\"  + arch + "\\Rscript.exe"
    else:
        Rscript = RBoxSettings("Rscript", "Rscript")

    return Rscript

def check_output(args):
    try:
    	if sys.platform == "win32":
    		startupinfo = subprocess.STARTUPINFO()
    		startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    		output = subprocess.Popen(args, stdout=subprocess.PIPE, startupinfo=startupinfo).communicate()[0].decode('utf-8')
    	else:
    		output = subprocess.Popen(args, stdout=subprocess.PIPE).communicate()[0].decode('utf-8')
    except:
        print("Cannot locate Rscript, please provide the path to Rscript in the settings")
        output = ""

    return output


class RBoxStatusListener(sublime_plugin.EventListener):
    cache = {}
    last_row = 0

    def RStatusUpdater(self, view):
        point = view.sel()[0].end() if len(view.sel())>0 else 0
        if not view.score_selector(point, "source.r"):
            view.set_status("R-Box", "")
            return

        this_row = view.rowcol(point)[0]
        sel = view.sel()
        if len(sel)!=1: return
        if sel[0].begin() != sel[0].end(): return
        contentb = view.substr(sublime.Region(view.line(point).begin(), point))
        m = re.match(r".*?([a-zA-Z0-9.]+)\($", contentb)
        if not m: return
        view.set_status("R-Box", "")
        func = m.group(1)

        if func in self.cache:
            call = self.cache[func]
        else:
            Rscript = get_Rscript()
            plat = sublime.platform()
            args = [Rscript, '-e', 'args(' + func + ')']
            packages = RBoxSettings("packages", None)
            if packages: args.append('--default-packages=' + ",".join(packages))
            output = check_output(args)
            if not re.match("function ", output): return
            output = re.sub(r"^function ", "", output)
            output = re.sub(r"\)[^)]*$", ")", output)
            output =re.sub(r"\s*\n\s*", " ", output)
            call = func + output
            self.cache.update({func: call})

        self.last_row = this_row
        view.set_status("R-Box", call)

    def on_modified(self, view):
        if view.is_scratch() or view.settings().get('is_widget'): return
        point = view.sel()[0].end() if len(view.sel())>0 else 0
        if not view.score_selector(point, "source.r"):
            return
        # run it in another thread
        sublime.set_timeout(lambda : self.RStatusUpdater(view), 1)

    def on_selection_modified(self,view):
        if view.is_scratch() or view.settings().get('is_widget'): return
        point = view.sel()[0].end() if len(view.sel())>0 else 0
        if not view.score_selector(point, "source.r"):
            return
        this_row = view.rowcol(point)[0]
        if this_row!= self.last_row: view.set_status("R-Box", "")


    def on_post_save(self, view):
        if view.is_scratch() or view.settings().get('is_widget'): return
        point = view.sel()[0].end() if len(view.sel())>0 else 0
        if not view.score_selector(point, "source.r"):
            return
        self.obtain_func_call(view)

    def on_load(self, view):
        if view.is_scratch() or view.settings().get('is_widget'): return
        point = view.sel()[0].end() if len(view.sel())>0 else 0
        if not view.score_selector(point, "source.r"):
            return
        self.obtain_func_call(view)

    def on_activated(self, view):
        if view.is_scratch() or view.settings().get('is_widget'): return
        point = view.sel()[0].end() if len(view.sel())>0 else 0
        if not view.score_selector(point, "source.r"):
            return
        self.obtain_func_call(view)
        # print(self.cache)

    def obtain_func_call(self, view):
        funcsel = view.find_all(r"""\b(?:[a-zA-Z0-9._:]*)\s*(?:<-|=)\s*function\s*(\((?:(["\'])(?:[^\\]|\\.)*?\2|#.*$|[^()]|(?1))*\))""")
        for s in funcsel:
            m = re.match(r"^([^ ]+)\s*(?:<-|=)\s*(?:function)\s*(.+)$", view.substr(s))
            if m:
                self.cache.update({m.group(1): m.group(1)+m.group(2)})
