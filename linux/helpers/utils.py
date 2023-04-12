"""Contains utility functions."""

from functools import wraps
from logging import exception as logException
from logging import info as logInfo
from subprocess import run
from typing import Any, Callable, List, Optional
from warnings import warn

from linux.helpers.constants import COLOR_TERMINATOR, GREEN_BG_BLACK_FG, YELLOW_BG_BLACK_FG
from linux.type_definitions import InstallationStepReturnValueT


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


def runWithFish(*args: str) -> None:
    """Runs a command with fish.

    Raises:
        CalledProcessError: If the command execution failed.
    """
    run(["fish", "-c", *args], check=True)


def warnAboutUnsupportedConfig(key: str) -> None:
    """Warns that an unsupported key contains a value in the configuration.

    Raises:
        ValueError: If `key` is an empty string.
    """
    if not key:
        raise ValueError("`key` cannot be an empty string.")
    warn(
        f'{YELLOW_BG_BLACK_FG}Configuration contains a value for "{key}", but this key is not '
        f"supported for this OS.{COLOR_TERMINATOR}"
    )
