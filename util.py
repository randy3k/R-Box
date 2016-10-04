import re
import json
import sublime
import os


def look_up_packages(view):
    packages = [
        "base",
        "stats",
        "methods",
        "utils",
        "graphics",
        "grDevices"
    ]
    for s in [view.substr(s) for s in view.find_all("(?:library|require)\(([^)]*?)\)")]:
        m = re.search(r"""\((?:"|')?(.*?)(?:"|')?\)""", s)
        if m:
            packages.append(m.group(1))

    for s in [view.substr(s)
              for s in view.find_all("([a-zA-Z][a-zA-Z0-9.]*)(?=::(:)?[a-zA-Z0-9.]*)")]:
        packages.append(s)

    packages = list(set(packages))

    return packages


def load_package_file(pkg):
    data = None

    jsonFilepath = "/".join(['Packages', 'R-Box', 'packages', '%s.json' % pkg])
    try:
        data = json.loads(sublime.load_resource(jsonFilepath))
    except IOError:
        pass

    if data:
        return data

    jsonFilepath = os.path.join(sublime.packages_path(), "User",
                                'R-Box', 'packages', '%s.json' % pkg)
    if os.path.exists(jsonFilepath):
        with open(jsonFilepath, "r") as f:
            data = json.load(f)

    return data


def function_at_point(view, point):
    func = None
    nextpoint = view.line(point).begin()
    while True:
        nextm = view.find(r"""[a-zA-Z.][a-zA-Z0-9._]*"""
                          r"""(\((?:(["\'])(?:[^\\]|\\.)*?\2|#.*$|[^()]|(?1))*\))""",
                          nextpoint)
        if nextm.begin() == -1 or nextm.begin() > point:
            break
        else:
            thism = view.find(r"""[a-zA-Z.][a-zA-Z0-9._]*(?=\()""", nextm.begin())
            if nextm.begin() <= point and nextm.end() >= point:
                func = view.substr(thism)
            nextpoint = thism.end()

    return func
