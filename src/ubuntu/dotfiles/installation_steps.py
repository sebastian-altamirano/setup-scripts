"""Contains functions to perform each of the steps that make up the installation script."""

from logging import error as logError
from logging import info as logInfo
from os.path import abspath as getAbsolutePath
from os.path import dirname as getDirectoryName
from os.path import join as joinPaths
from subprocess import run
from typing import List

from dotfiles.helpers.utils import copyConfiguration, installationStep, runWithFish, runWithSh
from dotfiles.type_definitions import ApplicationSettingsMapping

runWithoutLogging = run


@installationStep
def installFish() -> None:
    """Installs fish and changes the default shell to it."""
    runWithSh("sudo", "apt-add-repository", "-y", "ppa:fish-shell/release-3")
    runWithSh("sudo", "apt", "-y", "install", "fish")

    logInfo("Changing the default shell to fish...")
    runWithSh(
        "sudo",
        "chsh",
        "-s",
        run(["which", "fish"], capture_output=True, check=True, text=True).stdout.rstrip(),
        run(["whoami"], capture_output=True, check=True, text=True).stdout.rstrip(),
    )


@installationStep
def upgradeSystemDependencies() -> None:
    """Upgrades system packages using apt."""
    runWithSh("sudo", "apt", "update")
    runWithSh("sudo", "apt", "-y", "upgrade")


@installationStep
def installPackages() -> List[str]:
    """Installs packages and plugins and returns post-installation instructions."""
    postInstallationInstructions: List[str] = []

    logInfo("Installing fisher...")
    # Fisher is installed using an script because it requires `source`, which cannot be executed
    # with `subprocess.run`.
    fisherInstallationScriptPath = joinPaths(
        getDirectoryName(getAbsolutePath(__file__)), "scripts/install-fisher.fish"
    )
    runWithSh(fisherInstallationScriptPath)

    logInfo("Installing some plugins for fisher...")
    runWithFish("fisher", "install", "IlanCosman/tide@v5")
    postInstallationInstructions.append("Run `tide configure` to configure the aspect of fish.")
    runWithFish("fisher", "install", "jethrokuan/z")
    runWithFish("fisher", "install", "jorgebucaran/nvm.fish")

    logInfo("Installing Node LTS...")
    runWithFish("nvm", "install", "lts")
    runWithFish("set", "--universal", "nvm_default_version", "lts")
    runWithSh("npm", "i", "-g", "npm")

    logInfo("Installing Git...")
    runWithSh("sudo", "apt", "-y", "install", "git")

    return postInstallationInstructions


@installationStep
def installVSCodeExtensions(extensions: List[str]) -> None:
    """Installs extensions for VSCode."""
    extensionThatCouldNotBeInstalled = ""
    for extension in extensions:
        commandOutput = runWithoutLogging(
            ["code", "--install-extension", extension], capture_output=True, check=True
        )
        if commandOutput.stderr:
            extensionThatCouldNotBeInstalled += f"- {extension}\n"

    if extensionThatCouldNotBeInstalled:
        logError(
            "Could not install the following extensions:\n%s",
            extensionThatCouldNotBeInstalled,
        )
    else:
        logInfo("All extensions have been installed successfully.")


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
