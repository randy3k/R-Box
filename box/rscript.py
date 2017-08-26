import sublime
import re
import os
import subprocess
from .settings import r_box_settings

ANSI_ESCAPE = re.compile(r'(\x9B|\x1B\[)[0-?]*[ -/]*[@-~]')


class ScriptMixin:
    message_shown = False

    def find_working_dir(self):
        if hasattr(self, "window"):
            view = self.window.active_view()
        elif hasattr(self, "view"):
            view = self.view
        else:
            view = None

        if view and view.file_name():
            file_dir = os.path.dirname(view.file_name())
            if os.path.isdir(file_dir):
                return file_dir

        window = view.window() if view else None
        if window:
            folders = window.folders()
            if folders and os.path.isdir(folders[0]):
                return folders[0]

        return None

    def custom_env(self):
        paths = r_box_settings.additional_paths()
        if sublime.platform() == "osx":
            paths += ["/Library/TeX/texbin", "/usr/local/bin"]
        env = os.environ.copy()
        if paths:
            sep = ";" if sublime.platform() == "windows" else ":"
            env["PATH"] = env["PATH"] + sep + sep.join(paths)
        return env

    def rcmd(self, script=None, file=None, args=None):
        cmd = [r_box_settings.rscript_binary()]
        if script:
            cmd = cmd + ["-e", script]
        elif file:
            cmd = cmd + [file]
        if args:
            cmd = cmd + args

        if sublime.platform() == "windows":
            # make sure console does not come up
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        else:
            startupinfo = None

        working_dir = self.find_working_dir()
        custom_env = self.custom_env()

        try:
            p = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=working_dir,
                env=custom_env,
                startupinfo=startupinfo)

            stdout, stderr = p.communicate()
            stdout, stderr = stdout.decode(), stderr.decode()

            if p.returncode == 0:
                return ANSI_ESCAPE.sub('', stdout)
            else:
                raise Exception(
                    "Failed to execute RScript with the following output:\n\n{}".format(stderr))

        except FileNotFoundError as e:
            if not self.message_shown:
                sublime.message_dialog(
                    "Rscript binary cannot be found automatically. "
                    "The path to `Rscript` can be specified in the R-Box settings.")
                self.message_shown = True
            raise Exception("Rscript binary not found.")

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

    def format_code(self, code, indent=4, width_cutoff=100):
        formatted_code = self.rcmd(
            "formatR::tidy_source(text=commandArgs(TRUE)[1], "
            "                     indent={:d}, width.cutoff={:d})".format(indent, width_cutoff),
            args=[code])

        return formatted_code[0:-1]

    def detect_free_vars(self, code):
        result = self.rcmd(
            "eval(parse(text=commandArgs(TRUE)[1]))",
            args=[sublime.load_resource("Packages/R-Box/box/detect_free_vars.R"), code]
        ).strip()
        return [s.strip() for s in result.split("\n")] if result else []
