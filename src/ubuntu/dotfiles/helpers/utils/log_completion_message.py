"""Defines a utility function to log a completion message with post-installation instructions."""

from logging import info as logInfo
from typing import List, Optional

from dotfiles.helpers.constants import COLOR_TERMINATOR, GREEN_BACKGROUND_BLACK_FOREGROUND


def logCompletionMessage(postInstallationInstructions: Optional[List[str]] = None) -> None:
    """Logs a completion message and post-installation instructions, if any."""
    logInfo("%sFinished!%s", GREEN_BACKGROUND_BLACK_FOREGROUND, COLOR_TERMINATOR)
    if postInstallationInstructions:
        logInfo("Now there are some manual steps you need to perform:")
        for instruction in postInstallationInstructions:
            logInfo("- %s", instruction)
