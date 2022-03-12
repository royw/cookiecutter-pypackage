"""The application.

Usage::

    cli = CLI()
    cli.execute(App())
"""

import argparse
from test_project.graceful_interrupt_handler import GracefulInterruptHandler

__docformat__ = 'restructuredtext en'


class App(object):
    """This is the application class."""

    # noinspection PyUnresolvedReferences,PyMethodMayBeStatic
    def execute(self, settings: argparse.Namespace) -> None:
        """Execute the tasks specified in the settings object.

        :param settings: the application settings
        :raises: ArgumentError
        """
        # TODO: Initialize logger if necessary

        with GracefulInterruptHandler() as handler:
            # TODO: implement app here
            if handler.interrupted:
                pass

        return None
