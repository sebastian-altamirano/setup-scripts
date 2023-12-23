"""Defines an installation step for installing Fish."""

from logging import info as logInfo
from subprocess import run

from dotfiles.helpers.utils import installationStep, runWithSh

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
        runWithoutLogging(
            ["which", "fish"], capture_output=True, check=True, text=True
        ).stdout.rstrip(),
        runWithoutLogging(["whoami"], capture_output=True, check=True, text=True).stdout.rstrip(),
    )
