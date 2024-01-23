"""Installation script for Ubuntu dotfiles."""

from json import loads as readJson
from pathlib import Path
from typing import List
from typing import get_type_hints as getTypeHints

from dotfiles import installation_steps as installationSteps
from dotfiles.helpers.utils import (
    DOTFILES_SETTINGS_FILE_PATH,
    logCompletionMessage,
    warnAboutUnsupportedOrUnrecognizedConfig,
)
from dotfiles.type_definitions import Config


def install() -> None:
    """Installs Ubuntu dotfiles.

    Upgrades dependencies, installs packages and copies applications settings.
    """
    postInstallationInstructions: List[str] = []

    installationSteps.upgradeSystemDependencies()
    installationSteps.installFish()
    postInstallationInstructions += installationSteps.installPackages()

    config: Config = readJson(Path(DOTFILES_SETTINGS_FILE_PATH).read_text(encoding="utf-8"))

    # Issue the warning before starting to do any work.
    supportedConfigurationKeys = getTypeHints(Config).keys()
    for key in config:
        if key not in supportedConfigurationKeys:
            warnAboutUnsupportedOrUnrecognizedConfig(key)

    if "vscodeExtensions" in config:
        installationSteps.installVSCodeExtensions(config["vscodeExtensions"])
    if "settingsPaths" in config:
        postInstallationInstructions += installationSteps.copyApplicationSettings(
            config["settingsPaths"]
        )

    # This step must be executed after `copyApplicationSettings` in order not to lose the changes
    # in case the user adds `.gitconfig` to `settingsPaths`.
    if "git" in config:
        installationSteps.configureGit(**config["git"])

    if "postInstallationInstructions" in config:
        postInstallationInstructions += config["postInstallationInstructions"]
    logCompletionMessage(postInstallationInstructions)
