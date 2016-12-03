import re
import sublime
import os
import subprocess

if sublime.platform() == "windows":
    from winreg import OpenKey, QueryValueEx, HKEY_LOCAL_MACHINE, KEY_READ


class RscriptMixins:
    message_shown = False
    default_rscript_binary = "Rscript"
    envPATH = None

    if sublime.platform() == "osx":
        try:
            envPATH = subprocess.check_output(
                "/bin/bash -l -c 'echo $PATH'", shell=True).decode("utf-8")
        except:
            pass
    elif sublime.platform() == "windows":
        envPATH = None
        try:
            default_rscript_binary = os.path.join(QueryValueEx(
                OpenKey(HKEY_LOCAL_MACHINE, "Software\\R-Core\\R", 0, KEY_READ),
                "InstallPath")[0], "bin", "Rscript.exe")
        except:
            pass

    def rscript(self, script=None, file=None, *args):
        rscript_binary = self.rbox_settings("rscript_binary", self.default_rscript_binary)
        my_env = os.environ.copy()
        if self.envPATH:
            my_env["PATH"] = my_env["PATH"] + ":" + self.envPATH
        cmd = [rscript_binary]
        if script:
            cmd = cmd + ["-e", script]
        elif file:
            cmd = cmd + [file]

        cmd = cmd + list(args)

        try:
            if sublime.platform() == "windows":
                # make sure console does not come up
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                return subprocess.check_output(
                    cmd, startupinfo=startupinfo, env=my_env).decode("utf-8")
            else:
                return subprocess.check_output(cmd, env=my_env).decode("utf-8")
        except FileNotFoundError as e:
            print("Rscript binary not found.")
            if not self.message_shown:
                sublime.message_dialog(
                    "Rscript binary cannot be found automatically."
                    "The path to `Rscript` can be specified in the R-Box settings.")
                self.message_shown = True
            return ""

    def list_installed_packages(self):
        return self.rscript("cat(rownames(installed.packages()))").strip().split(" ")

    def list_package_objects(self, pkg, exported_only=True):
        if exported_only:
            objects = self.rscript("cat(getNamespaceExports(asNamespace('{}')))".format(pkg))
        else:
            objects = self.rscript("cat(objects(asNamespace('{}')))".format(pkg))
        return objects.strip().split(" ")

    def show_function(self, pkg, funct):
        out = self.rscript("args({}:::{})".format(pkg, funct))
        out = re.sub(r"^function ", funct, out).strip()
        out = re.sub(r"NULL(?:\n|\s)*$", "", out).strip()
        return out

    def show_function_args(self, pkg, funct):
        out = self.rscript("cat(names(formals({}:::{})))".format(pkg, funct))
        return out.strip().split(" ")


class RBoxSettingsMixins:
    def rbox_settings(self, key, default):
        s = sublime.load_settings('R-Box.sublime-settings')
        ret = s.get(key, default)
        return ret if ret else default


class RBoxViewMixins:
    VALIDCALL = re.compile(r"(?:([a-zA-Z][a-zA-Z0-9.]*)(?::::?))?([.a-zA-Z0-9_-]+)\s*\($")

    def function_name_at_point(self, view, pt):
        if not view.match_selector(pt-1, "meta.function-call.r"):
            return None, None
        scope_begin = view.extract_scope(pt-1).begin()
        if view.match_selector(scope_begin, "support.function.r, variable.function.r"):
            scope_begin = view.find("\(", scope_begin).begin() + 1
        line = self.extract_line(view, scope_begin, truncated=True)
        m = self.VALIDCALL.search(line)
        if m:
            return m.groups()
        else:
            return None, None

    def inline_packages_for_view(self, view):
        packages = []
        for s in view.find_all(r"""(library|require)\(["']?[a-zA-Z][a-zA-Z0-9.]*"""):
            pkg = packages.append(re.sub(r"""(library|require)\(["']?""", "", view.substr(s)))
            if pkg and pkg not in packages:
                packages.append(pkg)
        return packages

    def extract_line(self, view, pt, truncated=False):
        if truncated:
            row, _ = view.rowcol(pt)
            line_begin = view.text_point(row, 0)
            return view.substr(sublime.Region(line_begin, pt))
        else:
            return view.substr(view.line(pt))


class RBoxMixins(RBoxViewMixins, RscriptMixins, RBoxSettingsMixins):

    pass
