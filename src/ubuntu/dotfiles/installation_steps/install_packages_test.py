"""Contains tests for the installation step defined in `install_packages.py`."""

# pylint: disable=missing-function-docstring

from unittest import TestCase
from unittest.mock import Mock, call, patch

from dotfiles.installation_steps.install_packages import installPackages


@patch("dotfiles.installation_steps.install_packages.runWithFish")
@patch("dotfiles.installation_steps.install_packages.runWithSh")
@patch("dotfiles.installation_steps.install_packages.joinPaths")
class InstallPackagesTests(TestCase):
    """Contains tests for the `installPackages` function."""

    def testIfNodeLtsIsInstalledAndSetAsDefault(
        self,
        _mockJoinPaths: Mock,
        _mockRunWithSh: Mock,
        mockRunWithFish: Mock,
    ) -> None:
        installPackages()

        mockRunWithFish.assert_has_calls(
            [
                call("nvm", "install", "lts"),
                call("set", "--universal", "nvm_default_version", "lts"),
            ]
        )
