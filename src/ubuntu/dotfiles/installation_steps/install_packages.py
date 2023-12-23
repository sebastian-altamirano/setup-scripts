"""Defines an installation step for installing packages."""

from logging import info as logInfo
from os.path import abspath as getAbsolutePath
from os.path import dirname as getDirectoryName
from os.path import join as joinPaths
from typing import List

from dotfiles.helpers.utils import installationStep, runWithFish, runWithSh


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
