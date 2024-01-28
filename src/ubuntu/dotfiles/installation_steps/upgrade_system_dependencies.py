"""Defines an installation step for upgrading system dependencies."""

from dotfiles.helpers.decorators.installation_step import installationStep
from dotfiles.helpers.utils.run_with import runWithSh


@installationStep
def upgradeSystemDependencies() -> None:
    """Upgrades system packages using apt."""
    runWithSh("sudo", "apt", "update")
    runWithSh("sudo", "apt", "-y", "upgrade")
