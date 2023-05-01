"""Contains functions to perform each of the steps that make up the installation script."""

from logging import error as logError
from logging import info as logInfo
from os import makedirs as createDirectories
from os.path import abspath as getAbsolutePath
from os.path import dirname as getDirectoryName
from os.path import isabs as isAbsolutePath
from os.path import join as joinPaths
from shutil import copy2 as copyFile
from subprocess import run
from typing import List

from dotfiles.helpers.utils import installationStep, runWithFish
from dotfiles.type_definitions import ApplicationSettingsMapping


@installationStep
def installFish() -> None:
    """Installs fish and changes the default shell to it."""
    run(["sudo", "apt-add-repository", "-y", "ppa:fish-shell/release-3"], check=True)
    run(["sudo", "apt", "-y", "install", "fish"], check=True)

    logInfo("Changing the default shell to fish...")
    run(
        [
            "sudo",
            "chsh",
            "-s",
            run(["which", "fish"], capture_output=True, check=True, text=True).stdout.rstrip(),
            run(["whoami"], capture_output=True, check=True, text=True).stdout.rstrip(),
        ],
        check=True,
    )


@installationStep
def upgradeSystemDependencies() -> None:
    """Upgrades system packages using apt."""
    run(["sudo", "apt", "update"], check=True)
    run(["sudo", "apt", "-y", "upgrade"], check=True)


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
    run([fisherInstallationScriptPath], check=True)

    logInfo("Installing some plugins for fisher...")
    runWithFish("fisher", "install", "IlanCosman/tide@v5")
    postInstallationInstructions.append("Run `tide configure` to configure the aspect of fish.")
    runWithFish("fisher", "install", "jethrokuan/z")
    runWithFish("fisher", "install", "jorgebucaran/nvm.fish")

    logInfo("Installing Node LTS...")
    runWithFish("nvm", "install", "lts")
    runWithFish("set", "--universal", "nvm_default_version", "lts")
    run(["npm", "i", "-g", "npm"], check=True)

    logInfo("Installing Git...")
    run(["sudo", "apt", "-y", "install", "git"], check=True)

    return postInstallationInstructions


@installationStep
def installVSCodeExtensions(extensions: List[str]) -> None:
    """Installs extensions for VSCode."""
    extensionThatCouldNotBeInstalled = ""
    for extension in extensions:
        commandOutput = run(
            ["code", "--install-extension", extension], capture_output=True, check=True
        )
        if commandOutput.stderr:
            extensionThatCouldNotBeInstalled += f"- {extension}\n"

    if extensionThatCouldNotBeInstalled:
        logError(
            "Could not install the following extensions:\n%s",
            extensionThatCouldNotBeInstalled,
        )


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
        if not isAbsolutePath(settingsMapping["destination"]):
            # We could convert the relative path to absolute, but this could result in resources
            # being copied to unwanted locations, which is why this restriction is imposed.
            logError(
                'Could not copy "%s", an absolute path was expected for "destination", but "%s" '
                "was received.",
                settingsMapping["resourceName"],
                settingsMapping["destination"],
            )
            continue
        createDirectories(settingsMapping["destination"], exist_ok=True)
        copyFile(
            src=getAbsolutePath(f"app-settings/{settingsMapping['resourceName']}"),
            dst=settingsMapping["destination"],
        )

        if "completionCommands" in settingsMapping:
            for commandArgs in settingsMapping["completionCommands"]:
                run(commandArgs, check=True)

        if "postInstallationInstructions" in settingsMapping:
            postInstallationInstructions.append(settingsMapping["postInstallationInstructions"])

    return postInstallationInstructions
