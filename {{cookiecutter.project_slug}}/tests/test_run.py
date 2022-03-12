#!/usr/bin/env python
"""Tests for `{{ cookiecutter.pkg_name }}` package.

Assumes the --help outputs a string that contains both the project name and the phrase "usage:"
"""
from pathlib import Path
from subprocess import run, PIPE

import pytest


def test_run_main():
    """Verify running the src file works.

    python src/test_project/main.py --help

    Verify return code is 0 and the expected usage message is sent to stdout.
    """
    src_dir = Path(__file__).parent.parent / "src"
    completed_process = run(["python", str(src_dir / "{{cookiecutter.pkg_name}}/main.py"), "--help"], stdout=PIPE)
    assert completed_process.returncode == 0
    assert "{{cookiecutter.project_name}}" in completed_process.stdout.decode(encoding="utf-8")
    assert "usage:" in completed_process.stdout.decode(encoding="utf-8")


def test_run_module():
    """Verify running the module works.

    python -m test_project.main --help

    Verify return code is 0 and the expected usage message is sent to stdout.
    """
    completed_process = run(["python", "-m", "{{cookiecutter.pkg_name}}.main", "--help"])
    assert completed_process.returncode == 0
    assert "{{cookiecutter.project_name}}" in completed_process.stdout.decode(encoding="utf-8")
    assert "usage:" in completed_process.stdout.decode(encoding="utf-8")


def test_poetry_run():
    """Verify running via poetry works.

    poetry run test-project --help

    Verify return code is 0 and the expected usage message is sent to stdout.
    """
    completed_process = run(["poetry", "run", "{{cookiecutter.project_slug}}", "--help"])
    assert completed_process.returncode == 0
    assert "{{cookiecutter.project_name}}" in completed_process.stdout.decode(encoding="utf-8")
    assert "usage:" in completed_process.stdout.decode(encoding="utf-8")
