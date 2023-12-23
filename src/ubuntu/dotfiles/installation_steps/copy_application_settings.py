"""Defines an installation step for copying application settings."""

from logging import error as logError
from logging import info as logInfo
from typing import List

from dotfiles.helpers.utils import copyConfiguration, installationStep, runWithSh
from dotfiles.type_definitions import ApplicationSettingsMapping


@installationStep
def copyApplicationSettings(settingsMappings: List[ApplicationSettingsMapping]) -> List[str]:
    """Copies applications settings and return post-installation instructions."""
    postInstallationInstructions: List[str] = []

    for settingsMapping in settingsMappings:
        logInfo(
            'Copying "%s" to "%s"...',
            settingsMapping["resourceName"],
            settingsMapping["destination"],
        )

        try:
            copyConfiguration(settingsMapping["resourceName"], settingsMapping["destination"])
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
