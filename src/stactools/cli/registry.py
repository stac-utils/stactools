from pkgutil import ModuleInfo
from types import ModuleType
from typing import Callable, Iterator, List
from click import Command, Group


class Registry():
    """A registry for resources that are built-in or contributed by plugins."""

    def __init__(self) -> None:
        self._create_command_functions: List[Callable[[Group], Command]] = []

    def register_subcommand(
            self, create_command_function: Callable[[Group], Command]) -> None:
        self._create_command_functions.append(create_command_function)

    def get_create_subcommand_functions(
            self) -> List[Callable[[Group], Command]]:
        return self._create_command_functions[:]

    def load_plugins(self) -> None:
        """Discover all plugins and register their resources.
        Import each Python module within the stactools namespace package
        and call the register_plugin function at its root (if it exists).
        """
        import importlib
        import pkgutil
        import stactools

        # From https://packaging.python.org/guides/creating-and-discovering-plugins/#using-namespace-packages  # noqa
        def iter_namespace(ns_pkg: ModuleType) -> Iterator[ModuleInfo]:
            # Specifying the second argument (prefix) to iter_modules makes the
            # returned name an absolute name instead of a relative one. This allows
            # import_module to work without having to do additional modification to
            # the name.
            return pkgutil.iter_modules(ns_pkg.__path__, ns_pkg.__name__ + '.')

        discovered_plugins = {
            name: importlib.import_module(name)
            for finder, name, ispkg in iter_namespace(stactools)
        }

        for name, module in discovered_plugins.items():
            register_plugin = getattr(module, 'register_plugin', None)
            if register_plugin:
                register_plugin(self)
