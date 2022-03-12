"""Safely edit a file by creating a backup which will be restored on any error."""

import os
import re
import shutil
from contextlib import contextmanager
from tempfile import NamedTemporaryFile
from typing import Dict, Iterable, List, TextIO, Optional, IO

from {{ cookiecutter.pkg_name }}.touch import touch


# hitting mypy bug: https://github.com/python/mypy/issues/1317
@contextmanager     # type: ignore
def safe_edit(file_name: str, create: bool = False) -> Iterable[List]:
    """Edit a file using a backup.  On any exception, restore the backup.

    :param file_name: source file to edit
    :param create: create the file if it doesn't exist
    :yield: dict containing open file instances for input (files['in']) and output (files['out'])
    :raises: allows IO exceptions to propagate

    Usage::

        with safeEdit(fileName) as in_file, outfile:
            for line in in_file.readlines():
                # edit line
                out_file.write(line)
    """
    backup_name = file_name + "~"

    if create:
        touch(file_name)

    in_file: Optional[TextIO] = None
    tmp_file: Optional[IO] = None
    tf_name: Optional[str] = None
    try:
        if os.path.isfile(file_name):
            in_file = open(file_name, mode="r", encoding="utf-8")
        tmp_file = NamedTemporaryFile(mode="w", delete=False, encoding="utf-8")
        tf_name = tmp_file.name
        yield [in_file, tmp_file]

    # intentionally catching any exceptions
    # pylint: disable=W0702
    except Exception:
        # on any exception, delete the output temporary file
        if tmp_file:
            tmp_file.close()
            tmp_file = None
        if tf_name:
            os.remove(tf_name)
            tf_name = None
        raise
    finally:
        if in_file:
            in_file.close()
        if tmp_file:
            tmp_file.close()
        if tf_name:
            # ideally this block would be thread locked at os level
            # remove previous backup file if it exists
            # noinspection PyBroadException
            try:
                os.remove(backup_name)
            except Exception:
                pass

            # Note, shutil.move will safely move even across file systems

            # backup source file
            if os.path.isfile(file_name):
                shutil.move(file_name, backup_name)

            # put new file in place
            # noinspection PyTypeChecker
            shutil.move(tf_name, file_name)


def quick_edit(file_name: str, regex_replacement_dict: Dict[str, List[str]]) -> None:
    """This handles replacing text by using regular expressions.

    The simple case of replacing the first occurrence in each line of 'foo' with 'bar' is::

        quick_edit(file_name, {'foo': ['bar']})
        quick_edit(file_name, {r'.*?(foo).*': ['bar']})

    To replace 'foo' with 'bar' and 'car' with 'dog' in each line::

        quick_edit(file_name, {'foo': ['bar'],
                               'car': ['dog']})

    You can use multiple groups like:

        quick_edit(file_name, {r'.*?(foo).*?(car).*': ['bar', 'dog']})


    WARNING, there are probably gotchas here.

    :param file_name: file to edit
    :param regex_replacement_dict:
    """
    files: List
    with safe_edit(file_name) as files:
        # hitting mypy bug: https://github.com/python/mypy/issues/8829
        in_file = files[0]  # type: ignore
        out_file = files[1]  # type: ignore
        if in_file and out_file:
            for line in in_file.readlines():
                out_line = _line_replacement(line, regex_replacement_dict)
                out_file.write(out_line)


def _line_replacement(line: str, regex_replacement_dict: Dict[str, List[str]]) -> str:
    for regex in regex_replacement_dict.keys():
        line = _single_replacement(line, regex, regex_replacement_dict[regex])
    return line


def _single_replacement(line: str, regex: str, values: List[str]) -> str:
    newline = line
    if "(" not in regex:
        regex = ".*(" + regex + ").*"
    match = re.match(regex, line)
    if match:
        newline = ""
        postfix = ""
        for group in range(1, len(match.groups()) + 1):
            a = 0
            if group > 1:
                a = match.end(group - 1)
            newline += line[a: match.start(group)]
            newline += values[group - 1]
            postfix = line[match.end(group):]
        newline += postfix
    return newline
