"""Contains tests for the installation step defined in `install_fish.py`."""

# pylint: disable=missing-function-docstring

from unittest import TestCase
from unittest.mock import Mock, patch

from dotfiles.installation_steps.install_fish import installFish


@patch("dotfiles.installation_steps.install_fish.runWithSh")
class InstallFishTests(TestCase):
    """Contains tests for the `installFish` function."""

    def testIfFishIsConfiguredAsTheDefaultShell(
        self,
        mochRunWithSh: Mock,
    ) -> None:
        fishShellLocation = "/usr/bin/fish"
        user = "sebastian"

        def runWithShSideEffect(*args: str) -> Mock:
            if args == ("which", "fish"):
                return Mock(stdout=fishShellLocation)
            if args == ("whoami",):
                return Mock(stdout=user)
            return Mock()

        mochRunWithSh.side_effect = runWithShSideEffect

        installFish()

        mochRunWithSh.assert_called_with("sudo", "chsh", "-s", fishShellLocation, user)
