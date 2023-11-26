"""Contains utility functions."""

from functools import wraps
from logging import exception as logException
from logging import info as logInfo
from os import makedirs as createDirectories
from os.path import abspath as getAbsolutePath
from os.path import exists as pathExists
from os.path import isdir as isDirectory
from shutil import copy2 as copyFile
from shutil import copytree as copyDirectory
from subprocess import CompletedProcess, run
from typing import Any, Callable, List, Optional
from warnings import warn

from dotfiles.helpers.constants import COLOR_TERMINATOR, GREEN_BG_BLACK_FG, YELLOW_BG_BLACK_FG
from dotfiles.type_definitions import InstallationStepReturnValueT


def copyConfiguration(resourceName: str, destinationPath: str) -> None:
    """Copies a configuration resource to the specified destination.

    Args:
        resourceName: A resource (a file or a directory) located in the `/config/ubuntu` folder.
        destinationPath: A relative or absolute path where to copy the resource.

    Raises:
        FileNotFoundError: If the resource does not exist.
    """
    absoluteSourcePath = getAbsolutePath(f"../../../../config/ubuntu/{resourceName}")
    absoluteDestinationPath = getAbsolutePath(destinationPath)

    if not pathExists(absoluteSourcePath):
        raise FileNotFoundError()

    if isDirectory(absoluteSourcePath):
        copyDirectory(src=absoluteSourcePath, dst=absoluteDestinationPath, dirs_exist_ok=True)
    else:
        createDirectories(absoluteDestinationPath, exist_ok=True)
        copyFile(src=absoluteSourcePath, dst=absoluteDestinationPath)


def createFileWithContent(path: str, content: str) -> None:
    """Creates a file at the specified path with the specified content."""
    absolutePath = getAbsolutePath(path)
    createDirectories(absolutePath, exist_ok=True)
    with open(absolutePath, mode="w", encoding="utf-8") as file:
        file.write(content)


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
    logInfo("%sFinished!%s", GREEN_BG_BLACK_FG, COLOR_TERMINATOR)
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


def _runWith(*args: str) -> "CompletedProcess[str]":
    logInfo(*args)
    return run([*args], capture_output=True, check=True, text=True)


def runWithFish(*args: str) -> "CompletedProcess[str]":
    """Runs a command with fish.

    The command is logged before being executed.

    Raises:
        CalledProcessError: If the command execution failed.
    """
    return _runWith("fish", "-c", *args)


def runWithSh(*args: str) -> "CompletedProcess[str]":
    """Runs a command with sh.

    The command is logged before being executed.

    Raises:
        CalledProcessError: If the command execution failed.
    """
    return _runWith(*args)


def warnAboutUnsupportedOrUnrecognizedConfig(key: str) -> None:
    """Issues a warning about the presence of an unsupported/unrecognized key in the configuration.

    Raises:
        ValueError: If `key` is an empty string.
    """
    if not key:
        raise ValueError("`key` cannot be an empty string.")
    warn(
        f'{YELLOW_BG_BLACK_FG}The configuration contains a value for "{key}", but this key is '
        f"either not recognized or is not supported by this OS.{COLOR_TERMINATOR}"
    )
