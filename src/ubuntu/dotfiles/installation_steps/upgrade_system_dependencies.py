"""Defines an installation step for upgrading system dependencies."""

from dotfiles.helpers.utils import installationStep, runWithSh


@installationStep
def upgradeSystemDependencies() -> None:
    """Upgrades system packages using apt."""
    runWithSh("sudo", "apt", "update")
    runWithSh("sudo", "apt", "-y", "upgrade")
