"""A context manager base class that supports an optional config file and defaults for command line argument parsing.

To be useful, you must derive a class from this base class, and you should override at least the **_cli_options**
method.  You may find it useful to also override **_default_config_files** and **_cli_validate** methods.

This base class adds the following features to ArgumentParser:

* config file support from either the command line (-c|--conf_file FILE) or from expected locations (current
  directory then user's home directory).  The default config file name is created by prepending '.' and appending
  'rc' to the applications package name (example, app_package = 'foobar', then config file name would be
  '.foobarrc' and the search order would be: ['./.foobarrc', '~/.foobarrc']).

* display the application's version from app_package.version (usually defined in app_package/__init__.py).

* display the application's longhelp which is the module docstring in app_package/__init__.py.
"""
import argparse
import importlib
import os
import re
from configparser import ConfigParser, NoSectionError
from itertools import chain
from typing import Dict, List, Optional, Tuple

from logzero import logger

from {{ cookiecutter.pkg_name }}.safe_edit import safe_edit
from {{ cookiecutter.pkg_name }}.terminalsize import get_terminal_size


class SplitlineHelpFormatter(argparse.HelpFormatter):
    """Formatter that handles embedded newlines in help text."""

    def _split_lines(self, text: str, width: int) -> List[str]:
        """Splits a line on newlines.

        Extends the base method by splitting the line on newlines, then split the resulting lines
        using the base method.  Finally, the list of lists of strings is flattened into a list of strings
        which is returned.
        """
        # noinspection PyProtectedMember
        lines = [argparse.HelpFormatter._split_lines(self, line, width) for line in text.splitlines()]
        return list(chain.from_iterable(lines))


class ApplicationSettings(object):
    """Provide the base class for the application's settings.

    Usage::

        class MySettings(ApplicationSettings):
            HELP = {
                'foo': 'the foo option',
                'bar': 'the bar option',
            }

            def __init__(self):
                super(MySettings, self).__init__('App Name', 'app_package', ['APP Section'], self.HELP)

            def _cli_options(parser):
                parser.add_argument('--foo', action='store_true', help=self._help['foo'])
                parser.add_argument('--bar', action='store_true', help=self._help['bar'])

    Context Manager Usage::

        with MySettings() as settings:
            if settings.foo:
                pass

    Traditional Usage::

        parser, settings = MySettings().parse()
        if settings.foo:
            pass
    """

    VERSION_REGEX: str = r"__version__\s*=\s*[\'\"](\S+)[\'\"]"

    def __init__(
        self,
        app_name: str,
        app_package: str,
        config_sections: List,
        help_strings: Dict,
        config_files: Optional[List[str]] = None,
        persist: Optional[List[str]] = None,
    ) -> None:
        """Initialize.

        :param app_name: The application name
        :param app_package: The application's package name
        :param config_sections: The INI sections in the config file to import in as defaults to the argument parser.
        :param help_strings: A dictionary that maps argument names to the argument's help message.
        :param config_files: A list of config files to load
        :param persist: A list of config items to persist
        """
        self.__app_name = app_name
        self.__app_package = app_package
        self.__config_sections = config_sections
        self.__config_files = config_files
        self.__persist = persist
        self._parser: argparse.ArgumentParser
        self._settings: argparse.Namespace
        self._remaining_argv: List[str]

        default_help = {
            "version": "Show the application's version.  (default: %(default)s)",
            "longhelp": "Verbose help message.  (default: %(default)s)",
        }

        self._help = default_help.copy()
        self._help.update(help_strings.copy())

    def parse(self) -> Tuple[argparse.ArgumentParser, argparse.Namespace, List[str]]:
        """Perform the parsing of the optional config files and the command line arguments.

        :return: the parser, the settings, any leftover arguments
        """
        config_parser_help = "Configuration file in INI format (default: {files})".format(
            files=self._default_config_files()
        )
        conf_parser = argparse.ArgumentParser(add_help=False)
        conf_parser.add_argument("-c", "--conf_file", metavar="FILE", help=config_parser_help)

        args, remaining_argv = conf_parser.parse_known_args()

        config_files = self.__config_files
        if config_files is None:
            config_files = self._default_config_files()[:]
        if args.conf_file:
            config_files.insert(0, args.conf_file)

        config = ConfigParser()
        config.read(config_files)
        defaults = {}
        if self.__persist is not None:
            for key in self.__persist:
                defaults[key] = ""
        for section in self.__config_sections:
            try:
                defaults.update(dict(config.items(section)))
            except NoSectionError:
                pass

        parent_parsers = [conf_parser] + self._cli_parent_parsers()

        # HACK:  ArgumentParser by default uses env['COLUMNS'] which is always 80, so we get the terminal
        # size and pass the console width into the HelpFormatter as the width.
        # TODO:  Currently hard coded the max_help_position.  This really should be dynamically calculated.
        (console_width, console_height) = get_terminal_size()
        parser = argparse.ArgumentParser(
            self.__app_name,
            parents=parent_parsers,
            formatter_class=lambda prog: SplitlineHelpFormatter(prog, max_help_position=30, width=console_width),
            description=self._help[self.__app_name],
        )

        if defaults is not None:
            parser.set_defaults(**defaults)

        self._cli_options(parser, defaults)

        settings, leftover_argv = parser.parse_known_args(remaining_argv)
        settings.config_files = config_files

        if self.__persist is not None and self.__persist:
            self._persist(settings, config_files, self.__persist)

        return parser, settings, leftover_argv

    def _persist(
        self,
        settings: argparse.Namespace,
        config_files: List[str],
        persist: Optional[List[str]],
    ) -> None:
        """Persist config items to config files."""
        existing_files = [file_ for file_ in config_files if os.path.isfile(file_)]
        existing_files.append(config_files[0])
        files: List
        with safe_edit(existing_files[0]) as files:
            # hitting mypy bug: https://github.com/python/mypy/issues/8829
            out_file = files[1]  # type: ignore
            out_file.write("[{app}]\n".format(app=self.__app_name))
            if persist:
                for key in persist:
                    out_file.write("{key}={value}\n".format(key=key, value=vars(settings)[key]))

    def _default_config_files(self) -> List[str]:
        """Defines the default set of config files to try to use.

        The default set is "./.{{cookiecutter.pkg_name}}rc",
        "~/.{{cookiecutter.pkg_name}}/{{cookiecutter.pkg_name}}.conf"
        and "~/.{{cookiecutter.pkg_name}}rc".

        You may override this method if you want to use a different set of config files.

        :return: the set of config file locations
        """
        rc_name = ".{{cookiecutter.pkg_name}}rc".format(pkg=self.__app_package)
        conf_name = os.path.expanduser("~/.{{cookiecutter.pkg_name}}/{{cookiecutter.pkg_name}}.conf".format(pkg=self.__app_package))
        home_rc_name = os.path.expanduser("~/.{{cookiecutter.pkg_name}}rc".format(pkg=self.__app_package))
        return [rc_name, conf_name, home_rc_name]

    # noinspection PyMethodMayBeStatic
    def _cli_parent_parsers(self) -> List[argparse.ArgumentParser]:
        """This is where you should add any parent parsers for the main parser.

        :return: a list of parent parsers
        """
        return []

    # noinspection PyUnusedLocal
    def _cli_options(self, parser: argparse.ArgumentParser, defaults: Dict[str, str]) -> None:
        """This is where you should add arguments to the parser.

        You should override this method.

        Default is a version argument (-v or --version) and a long help (--longhelp) which is the contents
        of the top level package. "{{cookiecutter.pkg_name}}", docstring.

        :param parser: the argument parser with --conf_file already added.
        :param defaults: the default dictionary usually loaded from a config file
        """
        parser.add_argument(
            "-v",
            "--version",
            dest="version",
            action="store_true",
            help=self._help["version"],
        )

        parser.add_argument(
            "--longhelp",
            dest="longhelp",
            action="store_true",
            help=self._help["longhelp"],
        )

    # noinspection PyMethodMayBeStatic,PyUnusedLocal
    def _cli_validate(self, settings: argparse.Namespace, remaining_argv: List[str]) -> Optional[str]:
        """This provides a hook for validating the settings after the parsing is completed.

        :param settings: the settings object returned by ArgumentParser.parse_args()
        :return: the error message if any
        """
        return None

    def __enter__(self, early_validate: bool = False) -> argparse.Namespace:
        """Context manager enter.

        :param early_validate: asserted if you want cli validation before longhelp and version handling
        :return: the settings namespace
        """
        self._parser, self._settings, self._remaining_argv = self.parse()

        # Logger.set_verbose(not self._settings.quiet)
        # Logger.set_debug(self._settings.debug)

        if early_validate:
            error_message = self._cli_validate(self._settings, self._remaining_argv)
            if error_message is not None:
                self._parser.error("\n" + error_message)

        if self._settings.longhelp:
            app_module = importlib.import_module(self.__app_package)
            logger.info(app_module.__doc__)
            exit(0)

        if self._settings.version:
            logger.info("Version %s" % self._load_version())
            exit(0)

        if not early_validate:
            error_message = self._cli_validate(self._settings, self._remaining_argv)
            if error_message is not None:
                self._parser.error("\n" + error_message)

        self._settings.parser = self._parser
        return self._settings

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        pass

    def _load_version(self) -> str:
        r"""Get the version from __init__.py.

        The file should contain a version line that matches::

            /^__version__\s*=\s*(\S+)/

        If it doesn't exist try to load it from the VERSION.txt file.

        If still no joy, then return 'Unknown'

        :returns: the version string or 'Unknown'
        """
        # noinspection PyBroadException
        try:
            return __import__(self.__app_package).__version__
        except Exception:
            pass

        path = os.path.dirname(__file__)
        print("_load_version path=>%s" % path)

        # trying __init__.py first
        try:
            file_name = os.path.join(path, "../__init__.py")
            # noinspection PyArgumentEqualDefault
            with open(file_name, "r") as in_file:
                for line in in_file.readlines():
                    match = re.match(self.VERSION_REGEX, line)
                    if match:
                        return match.group(1)
        except IOError:
            pass

        # no joy, so try getting the version from a deprecated VERSION.txt file.
        try:
            # noinspection PyUnresolvedReferences
            file_name = os.path.join(path, "VERSION.txt")
            # noinspection PyArgumentEqualDefault
            with open(file_name, "r") as in_file:
                return in_file.read().strip()
        except IOError:
            pass

        # no joy again, so return default
        return "Unknown"

    def help(self) -> int:
        """Let the parser print the help message.

        :return: 2
        """
        if self._parser:
            self._parser.print_help()
        return 2
