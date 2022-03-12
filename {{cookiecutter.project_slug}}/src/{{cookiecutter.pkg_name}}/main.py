#!/usr/bin/env python
"""This is the console entry point (from setup.py) for the application."""

# When called the sys.path may contain this files directory when it really needs the
# parent directory (example, from repo_root running "proj_package/main.py"), then this
# directory.  So we need to remove this directory and this directory's parent where ever
# they are in the sys.path, then insert this directory's parent followed by this directory
# into the start of sys.path.
#
# ::
#
#     Example file structure:
#
#     * repo_root
#     * repo_root/proj_package
#     * repo_root/proj_package/main.py
#
#     for the following to work:
#
#     cd repo_root
#     proj_package/main.py
#
#     then sys.path needs to be:
#
#         [repo_root, repo_root/proj_package, ...]

import os
import sys

__this_dir = os.path.abspath(os.path.dirname(__file__))
__parent_dir = os.path.dirname(__this_dir)
if __this_dir in sys.path:
    sys.path.remove(__this_dir)
if __parent_dir in sys.path:
    sys.path.remove(__parent_dir)
sys.path.insert(0, __parent_dir)
sys.path.insert(1, __this_dir)

from {{ cookiecutter.pkg_name }}.app import App     # noqa: E402 Module level import not at top of file
from {{ cookiecutter.pkg_name }}.cli import CLI     # noqa: E402 Module level import not at top of file


def main():
    """This is the console entry point."""
    cli = CLI()
    cli.execute(App())


if __name__ == '__main__':
    main()
