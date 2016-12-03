import sublime
import os
import re
import subprocess
if sublime.platform() == "windows":
    from winreg import OpenKey, QueryValueEx, HKEY_LOCAL_MACHINE, KEY_READ


def read_registry(key, valueex):
    reg_key = OpenKey(HKEY_LOCAL_MACHINE, key, 0, KEY_READ)
    return QueryValueEx(reg_key, valueex)


ANSI_ESCAPE = re.compile(r'(\x9B|\x1B\[)[0-?]*[ -/]*[@-~]')


def execute_command(cmd, env=None, *args):
    if not env:
        env = os.environ.copy()
    if sublime.platform() == "windows":
        # make sure console does not come up
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        out = subprocess.check_output(
            cmd, startupinfo=startupinfo, env=env, *args).decode("utf-8")
    else:
        out = subprocess.check_output(cmd, env=env, *args).decode("utf-8")

    return ANSI_ESCAPE.sub('', out)
