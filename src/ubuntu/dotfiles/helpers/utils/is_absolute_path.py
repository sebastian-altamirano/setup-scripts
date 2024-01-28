"""Defines a utility function to determine if a path is absolute."""

from os.path import expanduser as expandUser
from os.path import expandvars as expandVars
from os.path import isabs as isAbsolute


def isAbsolutePath(path: str) -> bool:
    """Checks if the given path is an absolute path or not.

    Args:
        path: An absolute or relative path. The path can contain the tilde character (~) to
            represent the user's home directory, as well as environment variables such as `$HOME`.
    """
    return isAbsolute(expandUser(expandVars(path)))
