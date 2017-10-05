import sublime_plugin
import re
from types import SimpleNamespace
from collections import OrderedDict
from .script_mixin import ScriptMixin
from .view_mixin import RBoxViewMixin
from .settings import r_box_settings


VALIDCOMPLETION = re.compile(r"[.a-zA-Z0-9_-]+$")


class PackageNamespace(SimpleNamespace):
    exported = []
    unexported = []


class NamespaceManager(ScriptMixin):
    ns = OrderedDict()
    fcall = {}
    fargs = {}
    _installed_packages = []

    def installed_packages(self):
        if not self._installed_packages:
            self._installed_packages = super().installed_packages()
        return self._installed_packages

    def get_namespace(self, pkg):
        if pkg in self.ns:
            return self.ns[pkg]

        if pkg in self.installed_packages():
            exported = self.list_package_objects(pkg, exported_only=True)
            unexported = list(
                set(self.list_package_objects(pkg, exported_only=False)) -
                set(exported))
            ns = PackageNamespace(exported=exported, unexported=unexported)
            self.ns.update({pkg: ns})
        else:
            ns = PackageNamespace()

        return ns

    def get_function_call(self, pkg=None, funct=None):
        if not pkg:
            pkg = self.find_object_in_packages(funct)
        if not pkg:
            return ""
        pkg_name = "{}:::{}".format(pkg, funct)
        if pkg_name in self.fcall:
            return self.fcall[pkg_name]

        fcall = super().get_function_call(pkg, funct)
        self.fcall[pkg_name] = fcall
        return fcall

    def list_function_args(self, pkg=None, funct=None):
        if not pkg:
            pkg = self.find_object_in_packages(funct)
        if not pkg:
            return []
        pkg_name = "{}:::{}".format(pkg, funct)
        if pkg_name in self.fargs:
            return self.fargs[pkg_name]

        fargs = super().list_function_args(pkg, funct)
        self.fargs[pkg_name] = fargs
        return fargs

    def find_object_in_packages(self, obj, all_packages=False):
        pkgs = []
        for pkg, ns in reversed(list(self.ns.items())):
            if obj in ns.exported or obj in ns.unexported:
                pkgs.append(pkg)
                if not all_packages:
                    break
        if all_packages:
            return pkgs
        else:
            return pkgs[0] if pkgs else None


namespace_manager = NamespaceManager()


class RBoxNameSpaceListener(RBoxViewMixin, sublime_plugin.EventListener):

    default_packages = [
        "base", "stats", "methods", "utils", "graphics", "grDevices"
    ]

    def should_load(self, view):
        if view.settings().get('is_widget'):
            return False

        try:
            pt = view.sel()[0].end()
        except Exception:
            pt = 0

        if not view.match_selector(pt, "source.r, source.r-console"):
            return False

        return r_box_settings.get("auto_completions", True) or \
            r_box_settings.get("show_popup_hints", True)

    def filter_completions(self, objects):
        return filter(lambda x: VALIDCOMPLETION.match(x), objects)

    def perpare_pkg_objects(self, pkg):
        ns = namespace_manager.get_namespace(pkg)
        filtered_exported = self.filter_completions(ns.exported)
        return [[obj + "\t{" + pkg + "}", obj] for obj in filtered_exported]

    def set_completions_for_view(self, view, packages):
        # TODO: ultilize loaded_packages to update completions
        completions = []
        packages = list(set(self.default_packages + packages))
        for pkg in packages:
            completions += self.perpare_pkg_objects(pkg)

        completions += [["{}\tInstalled Package".format(pkg), pkg]
                        for pkg in namespace_manager.installed_packages()]

        view.settings().set("R-Box.completions", completions)
        view.settings().set("R-Box.loaded_packages", packages)

    def refresh_completions_for_view(self, view):
        packages = self.inline_packages_for_view(view)
        self.set_completions_for_view(view, packages)

    def on_post_save_async(self, view):
        if self.should_load(view):
            self.refresh_completions_for_view(view)

    def on_load_async(self, view):
        if self.should_load(view):
            self.refresh_completions_for_view(view)

    def on_activated_async(self, view):
        if self.should_load(view):
            self.refresh_completions_for_view(view)
