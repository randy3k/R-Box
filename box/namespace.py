from types import SimpleNamespace
from collections import OrderedDict
from .script_mixin import ScriptMixin


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
            unexported = list(set(self.list_package_objects(pkg, exported_only=False)) -
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
