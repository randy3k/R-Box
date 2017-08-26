import re
import sublime
import os
from .utils import execute_command
from .settings import r_box_settings


class ScriptMixin:
    message_shown = False

    def custom_env(self):
        paths = r_box_settings.additional_paths()
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

        try:
            return execute_command(cmd, env=self.custom_env())
        except FileNotFoundError as e:
            print("Rscript binary not found.")
            if not self.message_shown:
                sublime.message_dialog(
                    "Rscript binary cannot be found automatically."
                    "The path to `Rscript` can be specified in the R-Box settings.")
                self.message_shown = True
            return None
        except Exception as e:
            print("R-Box:", e)
            raise e

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
