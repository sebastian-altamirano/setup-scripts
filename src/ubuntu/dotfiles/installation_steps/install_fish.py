"""Defines an installation step for installing Fish."""

from logging import info as logInfo

from dotfiles.helpers.utils import installationStep, runWithSh


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
        runWithSh("which", "fish").stdout.rstrip(),
        runWithSh("whoami").stdout.rstrip(),
    )
