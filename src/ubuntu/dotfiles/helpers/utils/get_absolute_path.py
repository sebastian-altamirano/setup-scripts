"""Defines a utility function to calculate an absolute path."""

from os.path import abspath as absolutePath
from os.path import expanduser as expandUser
from os.path import expandvars as expandVars


def getAbsolutePath(path: str) -> str:
    """Returns the absolute path of the given path.

    Args:
        path: An absolute or relative path, note that if the path is relative, it will be calculated
            relative to the CWD. The path can contain the tilde character (~) to represent the
            user's home directory, as well as environment variables such as `$HOME`.
    """
    return absolutePath(expandUser(expandVars(path)))
