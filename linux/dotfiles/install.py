"""Installation script for Linux dotfiles."""

from json import loads as readJson
from typing import List

from dotfiles.helpers.utils import logCompletionMessage, warnAboutUnsupportedConfig
from dotfiles.installation_steps import (
    copyApplicationSettings,
    installFish,
    installPackages,
    installVSCodeExtensions,
    upgradeSystemDependencies,
)
from dotfiles.type_definitions import Config

UNSUPPORTED_CONFIGURATION_KEYS = [
    # This is not supported because this program is intended to be run inside WSL.
    "quickAccessFolders"
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
    for key in UNSUPPORTED_CONFIGURATION_KEYS:
        if key in config:
            warnAboutUnsupportedConfig(key)
    if "vscodeExtensions" in config:
        installVSCodeExtensions(config["vscodeExtensions"])
    if "settingsPaths" in config:
        postInstallationInstructions += copyApplicationSettings(config["settingsPaths"])

    logCompletionMessage(postInstallationInstructions)
