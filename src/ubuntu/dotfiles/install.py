"""Installation script for Ubuntu dotfiles."""

from json import loads as readJson
from typing import List, get_type_hints

from dotfiles.helpers.utils import logCompletionMessage, warnAboutUnsupportedOrUnrecognizedConfig
from dotfiles.installation_steps import (
    configureGit,
    copyApplicationSettings,
    installFish,
    installPackages,
    installVSCodeExtensions,
    upgradeSystemDependencies,
)
from dotfiles.type_definitions import Config


def install() -> None:
    """Installs Ubuntu dotfiles.

    Upgrades dependencies, installs packages and copies applications settings.
    """
    postInstallationInstructions: List[str] = []

    upgradeSystemDependencies()
    installFish()
    postInstallationInstructions += installPackages()

    config: Config = readJson("settings.json")

    # Issue the warning before starting to do any work.
    supportedConfigurationKeys = get_type_hints(Config).keys()
    for key in config:
        if key not in supportedConfigurationKeys:
            warnAboutUnsupportedOrUnrecognizedConfig(key)

    if "vscodeExtensions" in config:
        installVSCodeExtensions(config["vscodeExtensions"])
    if "settingsPaths" in config:
        postInstallationInstructions += copyApplicationSettings(config["settingsPaths"])

    # This step must be executed after `copyApplicationSettings` in order not to lose the changes
    # in case the user adds `.gitconfig` to `settingsPaths`.
    if "git" in config:
        configureGit(**config["git"])

    if "postInstallationInstructions" in config:
        postInstallationInstructions += config["postInstallationInstructions"]
    logCompletionMessage(postInstallationInstructions)
