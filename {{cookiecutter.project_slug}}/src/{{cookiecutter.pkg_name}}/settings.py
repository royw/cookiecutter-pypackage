"""Settings adds application specific information to the generic ApplicationSettings class.

Usage::

    with Settings() as settings:
    try:
        app.execute(self, settings)
        exit(0)
    except ArgumentError as ex:
        error(str(ex))
        exit(1)
"""
import argparse
from typing import Dict, List, Optional

from {{ cookiecutter.pkg_name }}.application_settings import ApplicationSettings


class Settings(ApplicationSettings):
    """Where the project's options are defined."""

    HELP = {
        '{{cookiecutter.project_name}}': "{{cookiecutter.project_short_description}}",

        'info_group': '',
        'version': "Show {{cookiecutter.project_name}}'s version.",
        'longhelp': 'Long help about {{cookiecutter.project_name}}.',

        'output_group': 'Options that control generated output.',
        'verbosity': 'Set verbosity level: 0=none, 1=errors, 2=info+errors, 3+=debug+info+errors (default=2).',
        'logfile': 'File to log all messages (debug, info, warning, error, fatal) to.',
    }

    def __init__(self):
        """Initialize the base class."""
        super(Settings, self).__init__('{{cookiecutter.project_name}}', '{{cookiecutter.pkg_name}}',
                                       ['{{cookiecutter.project_name}}'], self.HELP)

    def _cli_options(self, parser: argparse.ArgumentParser, defaults: Dict) -> None:
        """Adds application specific arguments to the parser.

        :param parser: the argument parser with --conf_file already added.
        """
        info_group = parser.add_argument_group(title='Informational Commands', description=self._help['info_group'])
        info_group.add_argument('--version', dest='version', action='store_true', help=self._help['version'])
        info_group.add_argument('--longhelp', dest='longhelp', action='store_true', help=self._help['longhelp'])

        output_group = parser.add_argument_group(title='Output Options', description=self._help['output_group'])
        output_group.add_argument(
            '--verbosity', dest='verbosity', default=2, type=int, metavar='INT', help=self._help['verbosity']
        )
        output_group.add_argument('--logfile', type=str, metavar='FILE', help=self._help['logfile'])

    def _cli_validate(self, settings: argparse.Namespace, remaining_argv: List[str]) -> Optional[str]:
        """Verify we have required options for commands.

        :param settings: the settings object returned by ArgumentParser.parse_args()
        :return: the error message if any
        """
        return None
