"""Installation script for Linux dotfiles."""

from json import loads as readJson
from typing import List

from dotfiles.helpers.utils import logCompletionMessage, warnAboutUnsupportedOrUnrecognizedConfig
from dotfiles.installation_steps import (
    copyApplicationSettings,
    installFish,
    installPackages,
    installVSCodeExtensions,
    upgradeSystemDependencies,
)
from dotfiles.type_definitions import Config

SUPPORTED_CONFIGURATION_KEYS = [
    "settingsPaths",
    "vscodeExtensions"
    # `quickAccessFolders` is not supported because this program is intended to be run inside WSL.
]


def install() -> None:
    """Installs Linux dotfiles.

    Upgrades dependencies, installs packages and copies applications settings.
    """
    postInstallationInstructions: List[str] = []

    installFish()
    upgradeSystemDependencies()
    postInstallationInstructions += installPackages()

    config: Config = readJson("settings.json")

    # Issue the warning before starting to do any work.
    for key in config:
        if key not in SUPPORTED_CONFIGURATION_KEYS:
            warnAboutUnsupportedOrUnrecognizedConfig(key)

    if "vscodeExtensions" in config:
        installVSCodeExtensions(config["vscodeExtensions"])
    if "settingsPaths" in config:
        postInstallationInstructions += copyApplicationSettings(config["settingsPaths"])

    logCompletionMessage(postInstallationInstructions)
