"""Contains utility functions."""

from functools import wraps
from io import TextIOWrapper
from logging import exception as logException
from logging import info as logInfo
from os import makedirs as createDirectories
from os.path import abspath as absolutePath
from os.path import exists as pathExists
from os.path import expanduser as expandUser
from os.path import expandvars as expandVars
from os.path import isabs as isAbsolute
from os.path import isdir as isDirectory
from os.path import join as joinPaths
from shutil import copy2 as copyFile
from shutil import copytree as copyDirectory
from subprocess import CompletedProcess, run
from typing import Any, Callable, List, Optional
from warnings import warn

from dotfiles.type_definitions import InstallationStepReturnValueT

_YELLOW_BACKGROUND_BLACK_FOREGROUND = "\x1b[6;30;43m"
_GREEN_BACKGROUND_BLACK_FOREGROUND = "\x1b[6;30;42m"
_COLOR_TERMINATOR = "\x1b[0m"


def getAbsolutePath(path: str) -> str:
    """Returns the absolute path of the given path.

    Args:
        path: An absolute or relative path, note that if the path is relative, it will be calculated
            relative to the CWD. The path can contain the tilde character (~) to represent the
            user's home directory, as well as environment variables such as `$HOME`.
    """
    return absolutePath(expandUser(expandVars(path)))


_filePath = getAbsolutePath(__file__)
PROJECT_ROOT_PATH = getAbsolutePath(joinPaths(_filePath, "..", ".."))
"""Absolute path to `/src/ubuntu/dotfiles`."""
PROJECT_SCRIPTS_PATH = getAbsolutePath(joinPaths(PROJECT_ROOT_PATH, "scripts"))
"""Absolute path to `/src/ubuntu/dotfiles/scripts`."""
USER_SETTINGS_PATH = getAbsolutePath(
    joinPaths(PROJECT_ROOT_PATH, "..", "..", "..", "config", "ubuntu")
)
"""Absolute path to `/config/ubuntu`."""
DOTFILES_SETTINGS_FILE_PATH = getAbsolutePath(joinPaths(USER_SETTINGS_PATH, "..", "settings.json"))
"""Absolute path to `/config/settings.json`."""


def isAbsolutePath(path: str) -> bool:
    """Checks if the given path is an absolute path or not.

    Args:
        path: An absolute or relative path. The path can contain the tilde character (~) to
            represent the user's home directory, as well as environment variables such as `$HOME`.
    """
    return isAbsolute(expandUser(expandVars(path)))


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


def createOrUpdateFile(filePath: str, content: str) -> None:
    """Creates or updates the specified file with the given content.

    Args:
        filePath: A relative or absolute path to the file, note that if the path is relative, it
            will be calculated relative to the CWD.
        content: The content to write or append to the file.
    """
    absoluteFilePath = getAbsolutePath(filePath)

    def writeContent(file: TextIOWrapper, content: str) -> None:
        file.write(content)
        if not content.endswith("\n"):
            file.write("\n")

    if pathExists(absoluteFilePath):
        with open(absoluteFilePath, mode="r+", encoding="utf-8") as file:
            fileContent = file.read()
            if not fileContent.endswith("\n") and not len(fileContent) == 0:
                file.write("\n")

            writeContent(file, content)
    else:
        createDirectories(absoluteFilePath, exist_ok=True)
        with open(absoluteFilePath, mode="w", encoding="utf-8") as file:
            writeContent(file, content)


def formatConfigurationBlocks(configurationBlocks: List[List[str]]) -> str:
    """Formats the given configuration blocks into a single string."""
    filteredConfigurationBlocks = [
        configurationBlock
        for configurationBlock in configurationBlocks
        if configurationBlock
        if len(configurationBlock) > 0
    ]

    if len(filteredConfigurationBlocks) == 0:
        return ""

    return (
        "\n\n".join(
            ["\n".join(configurationBlock) for configurationBlock in filteredConfigurationBlocks]
        )
        + "\n"
    )


def logCompletionMessage(postInstallationInstructions: Optional[List[str]] = None) -> None:
    """Logs a completion message and post-installation instructions, if any."""
    logInfo("%sFinished!%s", _GREEN_BACKGROUND_BLACK_FOREGROUND, _COLOR_TERMINATOR)
    if postInstallationInstructions:
        logInfo("Now there are some manual steps you need to perform:")
        for instruction in postInstallationInstructions:
            logInfo("- %s", instruction)


def installationStep(
    function: Callable[..., InstallationStepReturnValueT]
) -> Callable[..., InstallationStepReturnValueT]:
    """Decorator to log the progress (start and completion/failure) of an installation step."""

    @wraps(function)
    def runInstallationStep(*args: Any, **kwargs: Any) -> InstallationStepReturnValueT:
        stepName = function.__name__
        logInfo("--- Starting step: `%s` ---", stepName)

        try:
            returnValue = function(*args, **kwargs)
        except Exception as exception:
            logException("--- Failed step: `%s` ---\n", stepName)
            raise exception

        logInfo("--- Finished step: `%s` ---\n", stepName)
        return returnValue

    return runInstallationStep


def _runWith(*args: str, pipedInput: Optional[str] = None) -> "CompletedProcess[str]":
    logInfo(*args)
    return run([*args], capture_output=True, check=True, input=pipedInput, text=True)


def runWithFish(*args: str, pipedInput: Optional[str] = None) -> "CompletedProcess[str]":
    """Runs a command with fish.

    The command is logged before being executed.

    Raises:
        CalledProcessError: If the command execution failed.
    """
    return _runWith("fish", "-c", *args, pipedInput=pipedInput)


def runWithSh(*args: str, pipedInput: Optional[str] = None) -> "CompletedProcess[str]":
    """Runs a command with sh.

    The command is logged before being executed.

    Raises:
        CalledProcessError: If the command execution failed.
    """
    return _runWith(*args, pipedInput=pipedInput)


def warnAboutUnsupportedOrUnrecognizedConfig(key: str) -> None:
    """Issues a warning about the presence of an unsupported/unrecognized key in the configuration.

    Raises:
        ValueError: If `key` is an empty string.
    """
    if not key:
        raise ValueError("`key` cannot be an empty string.")
    warn(
        f'{_YELLOW_BACKGROUND_BLACK_FOREGROUND}The configuration contains a value for "{key}", but '
        f"this key is either not recognized or is not supported by this OS.{_COLOR_TERMINATOR}"
    )
