import re
import sublime
import os
from .utils import execute_command, read_registry


class RBoxSettingsMixin:
    _rscript_binary = None
    _additional_paths = None

    def r_box_settings(self, key, default):
        s = sublime.load_settings('R-Box.sublime-settings')
        return s.get(key, default)

    def rscript_binary(self):
        rscript_binary = self.r_box_settings("rscript_binary", self._rscript_binary)
        if not rscript_binary:
            if sublime.platform() == "windows":
                try:
                    rscript_binary = os.path.join(
                        read_registry("Software\\R-Core\\R", "InstallPath")[0],
                        "bin",
                        "Rscript.exe")
                except:
                    pass
        if not rscript_binary:
            rscript_binary = "Rscript"
        self._rscript_binary = rscript_binary
        return rscript_binary

    def additional_paths(self):
        additional_paths = self.r_box_settings("additional_paths", [])
        if not additional_paths:
            additional_paths = self._additional_paths
        if not additional_paths:
            if sublime.platform() == "osx":
                additional_paths = execute_command(
                    "/usr/bin/login -fpql $USER $SHELL -l -c 'echo -n $PATH'", shell=True)
                additional_paths = additional_paths.strip().split(":")
        if not additional_paths:
            additional_paths = "Rscript"

        self._additional_paths = additional_paths
        return additional_paths


class RBoxViewMixin:
    VALIDCALL = re.compile(r"(?:([a-zA-Z][a-zA-Z0-9.]*)(?::::?))?([.a-zA-Z0-9_-]+)\s*\($")

    def function_name_at_point(self, view, pt):
        if not view.match_selector(pt, "meta.function-call.r"):
            return None, None
        scope_begin = view.extract_scope(pt).begin()
        if view.match_selector(scope_begin, "support.function.r, variable.function.r"):
            scope_begin = view.find("\(", scope_begin).begin() + 1
        line = self.extract_line(view, scope_begin, truncated=True)
        m = self.VALIDCALL.search(line)
        if m:
            return m.groups()
        else:
            return None, None

    def _render_from_mdpopups_view(self, view):
        mdpops_view = view.window().find_output_panel("mdpopups")
        var_scope = "source.r meta.function-call.r " \
            "meta.function-call.parameters.r variable.parameter.r "
        comma_scope = "source.r meta.function-call.r " \
            "meta.function-call.parameters.r punctuation.separator.parameters.r "
        regions = mdpops_view.find_by_selector(var_scope)
        regions = [r for r in regions if mdpops_view.scope_name(r.begin()) == var_scope]
        count = len(regions)
        for r in reversed(regions):
            sep_point = r.end()
            while True:
                pt = mdpops_view.find(",", sep_point)
                if pt.end() == -1:
                    sep_point = mdpops_view.size() - 1
                    break
                if mdpops_view.scope_name(pt.begin()) == comma_scope:
                    sep_point = pt.begin()
                    break
                sep_point = pt.begin() + 1
            mdpops_view.run_command(
                "r_box_replace_selection",
                {"region": (r.end(), sep_point),
                 "text": " = $%d" % count})
            count = count - 1
        return mdpops_view.substr(sublime.Region(0, mdpops_view.size()))

    def replace_function_at_point(self, view, point):
        text = self._render_from_mdpopups_view(view)
        text = " ".join([x.strip() for x in text.split("\n")])
        function_region = view.extract_scope(point)
        view.sel().clear()
        view.sel().add(function_region)
        view.run_command("insert_snippet", {"contents": text})

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


class RBoxMixins(RBoxViewMixin, RBoxSettingsMixin):

    pass


class RscriptMixin:
    message_shown = False

    def custom_env(self):
        paths = self.additional_paths()
        env = os.environ.copy()
        if paths:
            sep = ";" if sublime.platform() == "windows" else ":"
            env["PATH"] = env["PATH"] + sep + sep.join(paths)
        return env

    def rcmd(self, script=None, file=None, args=None):
        cmd = [self.rscript_binary()]
        if script:
            cmd = cmd + ["-e", script]
        elif file:
            cmd = cmd + [file]
        if args:
            cmd = cmd + args

        try:
            return execute_command(cmd, env=self.custom_env())
        except FileNotFoundError:
            print("Rscript binary not found.")
            if not self.message_shown:
                sublime.message_dialog(
                    "Rscript binary cannot be found automatically."
                    "The path to `Rscript` can be specified in the R-Box settings.")
                self.message_shown = True
            return ""
        except Exception as e:
            print("R-Box:", e)
            return ""

    def installed_packages(self):
        return self.rcmd("cat(rownames(installed.packages()))").strip().split(" ")

    def list_package_objects(self, pkg, exported_only=True):
        if exported_only:
            objects = self.rcmd("cat(getNamespaceExports(asNamespace('{}')))".format(pkg))
        else:
            objects = self.rcmd("cat(objects(asNamespace('{}')))".format(pkg))
        return objects.strip().split(" ")

    def get_function_call(self, pkg, funct):
        out = self.rcmd("args({}:::{})".format(pkg, funct))
        out = re.sub(r"^function ", funct, out).strip()
        out = re.sub(r"<bytecode: [^>]+>", "", out).strip()
        out = re.sub(r"NULL(?:\n|\s)*$", "", out).strip()
        return out

    def list_function_args(self, pkg, funct):
        out = self.rcmd("cat(names(formals({}:::{})))".format(pkg, funct))
        return out.strip().split(" ")
