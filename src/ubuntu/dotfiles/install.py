"""Installation script for Ubuntu dotfiles."""

from typing import List

from dotfiles import installation_steps as installationSteps
from dotfiles.helpers.utils.log_completion_message import logCompletionMessage
from dotfiles.type_definitions import Config


def install(config: Config) -> None:
    """Installs Ubuntu dotfiles.

    Upgrades dependencies, installs packages and copies applications settings.
    """
    postInstallationInstructions: List[str] = []

    installationSteps.upgradeSystemDependencies()
    installationSteps.installFish()
    postInstallationInstructions += installationSteps.installPackages()

    if "vscodeExtensions" in config:
        installationSteps.installVSCodeExtensions(config["vscodeExtensions"])
    if "settingsPaths" in config:
        postInstallationInstructions += installationSteps.copyApplicationSettings(
            config["settingsPaths"]
        )

    # This step must be executed after `copyApplicationSettings` in order not to lose the changes
    # in case the user adds `.gitconfig` to `settingsPaths`.
    if "git" in config:
        installationSteps.configureGit(config["git"])

    if "postInstallationInstructions" in config:
        postInstallationInstructions += config["postInstallationInstructions"]
    logCompletionMessage(postInstallationInstructions)
