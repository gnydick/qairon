import importlib
import os
import pkgutil


def __iter_namespace__(ns_pkg):
    # Specifying the second argument (prefix) to iter_modules makes the
    # returned name an absolute name instead of a relative one. This allows
    # import_module to work without having to do additional modification to
    # the name.
    return pkgutil.iter_modules([ns_pkg, ns_pkg + "."])


def discover_namespace(path):
    return __iter_namespace__(path)


def plugin_has_module(wanted_module, package):
    module = importlib.import_module(package)

    all_modules = [name for finder, name, ispkg in pkgutil.iter_modules(module.__path__) if ispkg]

    hazzes_module = list()

    for mod in all_modules:
        module_path = os.path.join(module.__path__[0], mod)
        sub_modules = [name for finder, name, ispkg in pkgutil.iter_modules([module_path])]
        if wanted_module in sub_modules:
            hazzes_module.append(mod)

    return hazzes_module
