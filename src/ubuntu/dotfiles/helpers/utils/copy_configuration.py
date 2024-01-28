"""Defines a utility function to copy resources from `/config/ubuntu` to a specified destination."""

from os import makedirs as createDirectories
from os.path import exists as pathExists
from os.path import isdir as isDirectory
from os.path import join as joinPaths
from shutil import copy2 as copyFile
from shutil import copytree as copyDirectory

from dotfiles.helpers.constants import USER_SETTINGS_PATH
from dotfiles.helpers.utils.get_absolute_path import getAbsolutePath


def copyConfiguration(resourceName: str, destinationPath: str) -> None:
    """Copies a configuration resource to the specified destination.

    Args:
        resourceName: A resource (a file or a directory) located in the `/config/ubuntu` folder.
        destinationPath: A relative or absolute path where to copy the resource, note that if the
            path is relative, it will be calculated relative to the CWD.

    Raises:
        FileNotFoundError: If the resource does not exist.
    """
    absoluteSourcePath = joinPaths(USER_SETTINGS_PATH, resourceName)
    absoluteDestinationPath = getAbsolutePath(destinationPath)

    if not pathExists(absoluteSourcePath):
        raise FileNotFoundError()

    if isDirectory(absoluteSourcePath):
        copyDirectory(src=absoluteSourcePath, dst=absoluteDestinationPath, dirs_exist_ok=True)
    else:
        createDirectories(absoluteDestinationPath, exist_ok=True)
        copyFile(src=absoluteSourcePath, dst=absoluteDestinationPath)
