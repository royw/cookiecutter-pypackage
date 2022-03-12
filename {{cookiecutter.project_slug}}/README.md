{% set is_open_source = cookiecutter.open_source_license != 'Not open source' -%}
# {{ cookiecutter.project_name }}

{% if is_open_source %}
[![pypi](https://img.shields.io/pypi/v/{{ cookiecutter.project_slug }}.svg)](https://pypi.org/project/{{ cookiecutter.project_slug }}/)
[![python](https://img.shields.io/pypi/pyversions/{{ cookiecutter.project_slug }}.svg)](https://pypi.org/project/{{ cookiecutter.project_slug }}/)
[![Build Status](https://github.com/{{ cookiecutter.github_username }}/{{ cookiecutter.project_slug }}/actions/workflows/dev.yml/badge.svg)](https://github.com/{{ cookiecutter.github_username }}/{{ cookiecutter.project_slug }}/actions/workflows/dev.yml)
[![codecov](https://codecov.io/gh/{{ cookiecutter.github_username }}/{{ cookiecutter.project_slug }}/branch/main/graphs/badge.svg)](https://codecov.io/github/{{ cookiecutter.github_username }}/{{ cookiecutter.project_slug }})

{% else %}
{% endif %}

{{ cookiecutter.project_short_description }}

{% if is_open_source %}
* Documentation: <https://{{ cookiecutter.github_username }}.github.io/{{ cookiecutter.project_slug }}>
* GitHub: <https://github.com/{{ cookiecutter.github_username }}/{{ cookiecutter.project_slug }}>
* PyPI: <https://pypi.org/project/{{ cookiecutter.project_slug }}/>
* Free software: {{ cookiecutter.open_source_license }}
{% endif %}

## Features

* Poetry package management
* Markdown documentation including project API
* Radon metrics (cyclomatic complexity, source lines of code) report in markdown documentation
* Black and ISort formatting
* mypy and flake8 linting
* src/package_name structure
* pytest and tox testing
* Helper scripts (in pyproject.toml and scripts/__init__.py)
* Settings Application Framework (SAF)

### Settings Application Framework

SAF is an object-orientated command line interface (CLI) framework that uses a "settings" object built from the CLI
arguments and passed to an application object that performs the work.  The settings object encapsulates the argument
parsing, validation, and help.  There is a CLI object if you want to use a Model View Controller (MVC) pattern but
most times that is overkill for a CLI app.

The main module is naturally the main entry point and creates the App and CLI instances, passing the App instance
to the CLI instance.

The CLI module creates the Settings instance which it passes to the App.execute method.

The App.execute method does the work, usually within a ^C handler (GracefulInterruptHandler) context.

The default SAF framework is runnable and supports --help, --version, and --longhelp arguments.

#### Support Modules

**application_settings** is the base class for Settings and encapsulates the parsing, including extended ArgParse
functionality such as config file support, persistence, and automatic terminal width support.  Basically the
pain points on using ArgParse are located here, allowing the Settings class to just define the groups and
arguments, and provide a post parsing hook for argument validation.

**graceful_interrupt_handler** is a context manager for capturing signal (i.e., ^C) easily.

**safe_edit** is a simple utility for editing files with a backup.

**terminalsize** is the multi-platform library for calculating the current terminal size.

**touch** a really simplistic touch utility.

### Click

A click_cli module is provided as a main entry point if you are using the click library.

## Prerequisites

* python 3.7+ (tested using pyenv). The pythonX.Y executables need to be on the path for tox to find them
* poetry
* cookiecutter

## Usage

Normal workflow

* Create project using cookiecutter
* Change to project directory
* Review pyproject.toml, mkdocs.yml, pydoc-markdown.yml
* poetry install
* To see available helper scripts: poetry run commands
* poetry run lint
* poetry run format
* poetry run tests
* poetry run metrics
* poetry run update_api_docs
* poetry run local_doc_server
* poetry build
* poetry run tox

Note, there is a makefile if you prefer to use make

## Credits

This package was created with [Cookiecutter](https://github.com/audreyr/cookiecutter) and the [waynerv/cookiecutter-pypackage](https://github.com/waynerv/cookiecutter-pypackage) project template.

* https://pydoc-markdown.readthedocs.io
* https://radon.readthedocs.io
* https://www.mkdocs.org
* https://python-poetry.org
*
