"""Console script for {{cookiecutter.pkg_name}}."""

{% if cookiecutter.command_line_interface|lower == 'saf' -%}
from {{ cookiecutter.pkg_name }}.settings import Settings
from logzero import logger


class ArgumentError(RuntimeError):
    """There is a problem with a command line argument."""

    pass


class CLI(object):
    """Command Line Interface for the App."""

    def execute(self, app):
        """Handle the command line arguments then execute the app.

        :param app: the application instance
        :type app: {package}.App
        """
        with Settings() as settings:
            try:
                results = app.execute(settings)
                if results is not None:
                    self.report(results)
                exit(0)
            except ArgumentError as ex:
                logger.error(str(ex))
                exit(1)

    # noinspection PyMethodMayBeStatic
    def report(self, results):
        """Generate the report.

        :param results: (success[], error[], missing_filters_for_rule_ids[])
        :type results: tuple
        """
        # TODO: implement result report
        logger.info(f"Results: {repr(results)}")

{%- endif %}
