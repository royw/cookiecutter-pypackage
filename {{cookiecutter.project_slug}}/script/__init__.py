import json
import os
import sys
from pathlib import Path
from textwrap import dedent

import toml
import logzero
from logzero import logger
from subprocess import call, run, PIPE
from jinja2 import Template

formatter = logzero.LogFormatter(fmt="%(color)s[%(levelname)1.1s %(asctime)s]%(end_color)s %(message)s")
logzero.setup_default_logger(formatter=formatter)


with open("pyproject.toml") as f:
    conf = toml.load(f)
__packages = conf["tool"]["poetry"]["packages"]

PACKAGE_NAME = __packages[0]["include"]
PACKAGE_PATH = os.path.join(__packages[0]["from"], PACKAGE_NAME)
END_POINTS = conf["tool"]["poetry"]["scripts"]
METRICS_MD = Path(__file__).parent / ".." / "docs" / "metrics.md"
API_MD = Path(__file__).parent / ".." / "docs" / "api.md"


def scripts():
    """List available scripts to run."""
    data = []
    for name, script in END_POINTS.items():
        funct = script.split(':')[-1]
        # assumes all functions are in this module,
        try:
            data.append([name, getattr(sys.modules[__name__], f"{funct}").__doc__ or ""])
        except AttributeError:
            logger.info(script)

    # two column output, first column the run endpoint, the second column is the docstring for the target function

    col0_width = max([len(row[0]) for row in data]) + 2
    col1_width = max([len(row[1]) for row in data]) + 2
    lines = []
    for row in data:
        lines.append(row[0].ljust(col0_width) + row[1].ljust(col1_width))

    logger.info("Available scripts:\n" + "\n".join(lines))


def reformat():
    """Format the source code."""
    logger.info("Running isort...")
    call(["isort", PACKAGE_PATH])
    logger.info("Running black...")
    call(["black", PACKAGE_PATH])


def lint():
    """Lint the source code."""
    logger.info("Running mypy...")
    call(["mypy", PACKAGE_PATH])
    logger.info("Running flake8...")
    call(["flake8", PACKAGE_PATH])


# def sphinx_api_document():
#     """Create source code documentation."""
#     opt = "-f" if os.path.exists(os.path.join("docs/api", "conf.py")) else "-F"
#     call(["sphinx-apidoc", opt, "-M", "-e", "-o", "docs/api", PACKAGE_PATH])
#     call(["make", "-C", "docs/api", "html"])
#
#
# def sphinx_test_document():
#     """Create unit test documentation."""
#     opt = "-f" if os.path.exists(os.path.join("docs/test", "conf.py")) else "-F"
#     call(["sphinx-apidoc", opt, "-M", "-e", "-o", "docs/test", "tests"])
#     call(["make", "-C", "docs/test", "html"])


def metrics():
    """Calculate code metrics."""
    logger.info("Analyze the given Python modules and compute Cyclomatic Complexity (CC).")
    cc_json = json.loads(run(["radon", "cc", "-s", "--json", PACKAGE_PATH], stdout=PIPE).stdout.decode("utf-8"))
    logger.info("Analyze the given Python modules and compute the Maintainability Index.")
    mi_json = json.loads(run(["radon", "mi", "-s", "--json", PACKAGE_PATH], stdout=PIPE).stdout.decode("utf-8"))
    logger.info("Analyze the given Python modules and compute raw metrics.")
    raw_json = json.loads(run(["radon", "raw", "-s", "--json", PACKAGE_PATH], stdout=PIPE).stdout.decode("utf-8"))

    {% raw %}
    template = Template(dedent("""
    # Code Metrics

    SLOC = Source Lines Of Code

    CC = Cyclomatic Complexity - rank (score)

    MI = Maintainability Index - rank (score)

    function, class, method = types

    {% for filename,values in cc_json.items() -%}
    {% set mi = "%d"|format(mi_json[filename]['mi']) -%}
    {% set file_name = filename|replace('_', '\\_') -%}
    ## {{file_name}} SLOC: {{raw_json[filename]['sloc']}} - MI: {{mi_json[filename]['rank']}} ({{mi}})

    {% for value in values -%}
    {% set name = value['name']|replace('_', '\\_') -%}
    * {{name}} {{value['type']}} CC: {{value['rank']}} ({{value['complexity']}})
    {% endfor -%}
    {% endfor %}
    """))
    {% endraw %}
    cc_markdown = template.render(cc_json=cc_json, mi_json=mi_json, raw_json=raw_json)
    with(open(METRICS_MD, "w", encoding="utf-8")) as output:
        output.write(cc_markdown)


def tests():
    """Run unit tests."""
    logger.info("Running pytest...")
    call(["pytest", "--html=report.html", f"--cov={PACKAGE_PATH}", "--cov-branch"])


def update_api_docs():
    """Update API Docs using pydoc-markdown."""
    logger.info("Generating API documents...")
    call(["pydoc-markdown"])
    {% raw %}
    with open(API_MD, "w", encoding="utf-8") as output:
        output.write(dedent("""
        {%
          include-markdown "../build/docs/content/api-documentation/test_project.md"
        %}
        """))
    {% endraw %}

def local_doc_server():
    """Run a local document server."""
    call(["poetry", "run", "mkdocs", "serve"])
