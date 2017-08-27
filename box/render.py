import sublime_plugin


class RBoxRenderRmarkdownCommand(sublime_plugin.TextCommand):
    def is_enabled(self):
        return self.view.settings().get("syntax").endswith("R Markdown.sublime-syntax")

    def run(self, edit):
        cmd = "rmarkdown::render(\"$file\", encoding = \"UTF-8\")"
        self.view.run_command("send_code", {"cmd": cmd})


class RBoxSweaveRnwCommand(sublime_plugin.TextCommand):
    def is_enabled(self):
        return self.view.settings().get("syntax").endswith("R Sweave.sublime-syntax")

    def run(self, edit):
        cmd = ("""setwd(\"$file_path\")\n"""
               """Sweave(\"$file\")\n"""
               """tools::texi2dvi(\"$file_base_name.tex\", pdf = TRUE)""")
        self.view.run_command("send_code", {"cmd": cmd})


class RBoxKnitRnwCommand(sublime_plugin.TextCommand):
    def is_enabled(self):
        return self.view.settings().get("syntax").endswith("R Sweave.sublime-syntax")

    def run(self, edit):
        cmd = ("""setwd(\"$file_path\")\n"""
               """knitr::knit(\"$file\", output=\"$file_base_name.tex\")\n"""
               """tools::texi2dvi(\"$file_base_name.tex\", pdf = TRUE)")""")
        self.view.run_command("send_code", {"cmd": cmd})
