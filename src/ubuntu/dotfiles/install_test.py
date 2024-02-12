"""Contains tests for the functions defined in `install.py`."""

# pylint: disable=missing-function-docstring

from unittest import TestCase
from unittest.mock import Mock, patch

from dotfiles.install import install
from dotfiles.type_definitions import Config


@patch("dotfiles.install.logCompletionMessage")
@patch("dotfiles.install.installationSteps")
class InstallTests(TestCase):
    """Contains tests for the `install` function."""

    def testIfAllConfigurationKeysAreOptional(  # pylint: disable=too-many-arguments
        self,
        mockInstallationSteps: Mock,
        mockLogCompletionMessage: Mock,
    ) -> None:
        emptyConfiguration: Config = {}

        install(emptyConfiguration)

        mockInstallationSteps.installFish.assert_called()
        mockInstallationSteps.upgradeSystemDependencies.assert_called()
        mockInstallationSteps.installPackages.assert_called()
        mockInstallationSteps.installVSCodeExtensions.assert_not_called()
        mockInstallationSteps.copyApplicationSettings.assert_not_called()
        mockLogCompletionMessage.assert_called()

    def testIfPostInstallationInstructionAreCollectedAndDisplayed(
        self,
        mockInstallationSteps: Mock,
        mockLogCompletionMessage: Mock,
    ) -> None:
        configurationPostInstalationInstructions = (
            "Post-installation instructions related to configuration restoration..."
        )
        configuration: Config = {
            "postInstallationInstructions": ["General post-installation instructions..."],
            "settingsPaths": [
                {
                    "resourceName": "fish",
                    "destination": "~/.config/fish",
                    "postInstallationInstructions": configurationPostInstalationInstructions,
                }
            ],
        }
        mockInstallPackages = mockInstallationSteps.installPackages
        mockCopyApplicationSettings = mockInstallationSteps.copyApplicationSettings
        mockInstallPackages.return_value = [
            "Post-installation instructions related to package installation..."
        ]
        mockCopyApplicationSettings.return_value = [configurationPostInstalationInstructions]
        expectedPostInstallationInstructions = [
            *mockInstallPackages.return_value,
            *mockCopyApplicationSettings.return_value,
            *configuration["postInstallationInstructions"],
        ]

        install(configuration)

        mockLogCompletionMessage.assert_called_once_with(expectedPostInstallationInstructions)
