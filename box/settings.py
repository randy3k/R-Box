import sublime
import os
from .utils import execute_command, read_registry


class RBoxSettings:
    _rscript_binary = None
    _additional_paths = []

    def get(self, key, default):
        s = sublime.load_settings('R-Box.sublime-settings')
        return s.get(key, default)

    def rscript_binary(self):
        rscript_binary = self.get("rscript_binary", self._rscript_binary)
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
        additional_paths = self.get("additional_paths", self._additional_paths)
        if not additional_paths:
            if sublime.platform() == "osx":
                additional_paths = execute_command(
                    "/usr/bin/login -fpql $USER $SHELL -l -c 'echo -n $PATH'", shell=True)
                additional_paths = additional_paths.strip().split(":")
        if not additional_paths:
            additional_paths = "Rscript"

        self._additional_paths = additional_paths
        return additional_paths


r_box_settings = RBoxSettings()
