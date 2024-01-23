"""Defines an installation step for copying application settings."""

from logging import error as logError
from logging import info as logInfo
from os.path import join as joinPaths
from typing import List

from dotfiles.helpers.utils import (
    DOTFILES_SETTINGS_FILE_PATH,
    copyConfiguration,
    getAbsolutePath,
    installationStep,
    isAbsolutePath,
    runWithSh,
)
from dotfiles.type_definitions import ApplicationSettingsMapping


@installationStep
def copyApplicationSettings(settingsMappings: List[ApplicationSettingsMapping]) -> List[str]:
    """Copies applications settings and return post-installation instructions."""
    postInstallationInstructions: List[str] = []

    for settingsMapping in settingsMappings:
        absoluteDestinationPath = getAbsolutePath(
            settingsMapping["destination"]
            if isAbsolutePath(settingsMapping["destination"])
            # If the path is relative I need to compute the absolute path relative to the
            # configuration file, otherwise the path will be calculated relative to the CWD.
            else joinPaths(DOTFILES_SETTINGS_FILE_PATH, settingsMapping["destination"])
        )

        logInfo(
            'Copying "%s" to "%s"...',
            settingsMapping["resourceName"],
            absoluteDestinationPath,
        )

        try:
            copyConfiguration(settingsMapping["resourceName"], absoluteDestinationPath)
        except FileNotFoundError:
            logError(
                'Could not copy "%s" because the resource does not exist.',
                settingsMapping["resourceName"],
            )

        if "completionCommands" in settingsMapping:
            logInfo("Running completion commands...")
            for commandArgs in settingsMapping["completionCommands"]:
                runWithSh(*commandArgs)

        if "postInstallationInstructions" in settingsMapping:
            postInstallationInstructions.append(settingsMapping["postInstallationInstructions"])

    return postInstallationInstructions
