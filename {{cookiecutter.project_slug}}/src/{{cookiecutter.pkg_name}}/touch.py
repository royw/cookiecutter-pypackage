"""Simple touch utility."""


def touch(filename: str) -> None:
    """Mimics the "touch filename" utility.

    :param filename: filename to touch
    """
    with open(filename, "a"):
        pass
