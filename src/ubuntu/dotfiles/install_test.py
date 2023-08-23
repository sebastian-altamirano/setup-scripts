"""Contains tests for the functions defined in `install.py`."""

# pylint: disable=missing-function-docstring

from unittest import TestCase
from unittest.mock import Mock, call, patch

from dotfiles.install import install
from dotfiles.type_definitions import Config


@patch("dotfiles.install.installFish")
@patch("dotfiles.install.upgradeSystemDependencies")
@patch("dotfiles.install.installPackages")
@patch("dotfiles.install.installVSCodeExtensions")
@patch("dotfiles.install.copyApplicationSettings")
@patch("dotfiles.install.warnAboutUnsupportedOrUnrecognizedConfig")
@patch("dotfiles.install.logCompletionMessage")
@patch("dotfiles.install.readJson")
class InstallTests(TestCase):
    """Contains tests for the `install` function."""

    def testIfAllConfigurationKeysAreOptional(  # pylint: disable=too-many-arguments
        self,
        mockReadJson: Mock,
        mockLogCompletionMessage: Mock,
        mockWarnAboutUnsupportedOrUnrecognizedConfig: Mock,
        mockCopyApplicationSettings: Mock,
        mockInstallVSCodeExtensions: Mock,
        mockInstallPackages: Mock,
        mockUpgradeSystemDependencies: Mock,
        mockInstallFish: Mock,
    ) -> None:
        emptyConfiguration: Config = {}
        mockReadJson.return_value = emptyConfiguration

        install()

        mockInstallFish.assert_called()
        mockUpgradeSystemDependencies.assert_called()
        mockInstallPackages.assert_called()
        mockWarnAboutUnsupportedOrUnrecognizedConfig.assert_not_called()
        mockInstallVSCodeExtensions.assert_not_called()
        mockCopyApplicationSettings.assert_not_called()
        mockLogCompletionMessage.assert_called()

    def testIfPostInstallationInstructionAreCollectedAndDisplayed(
        self,
        mockReadJson: Mock,
        mockLogCompletionMessage: Mock,
        _mockWarnAboutUnsupportedOrUnrecognizedConfig: Mock,
        mockCopyApplicationSettings: Mock,
        _mockInstallVSCodeExtensions: Mock,
        mockInstallPackages: Mock,
        _mockUpgradeSystemDependencies: Mock,
        _mockInstallFish: Mock,
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
        mockReadJson.return_value = configuration
        mockInstallPackages.return_value = [
            "Post-installation instructions related to package installation..."
        ]
        mockCopyApplicationSettings.return_value = [configurationPostInstalationInstructions]
        expectedPostInstallationInstructions = [
            *mockInstallPackages.return_value,
            *mockCopyApplicationSettings.return_value,
            *configuration["postInstallationInstructions"],
        ]

        install()

        mockLogCompletionMessage.assert_called_once_with(expectedPostInstallationInstructions)

    def testIfWarningsAreProducedForUnsupportedKeys(
        self,
        mockReadJson: Mock,
        _mockLogCompletionMessage: Mock,
        mockWarnAboutUnsupportedOrUnrecognizedConfig: Mock,
        _mockCopyApplicationSettings: Mock,
        _mockInstallVSCodeExtensions: Mock,
        _mockInstallPackages: Mock,
        _mockUpgradeSystemDependencies: Mock,
        _mockInstallFish: Mock,
    ) -> None:
        unsupportedConfiguration = {"unsupportedConfigurationKey": "Unsupported configuration"}
        mockReadJson.return_value = unsupportedConfiguration

        install()

        mockWarnAboutUnsupportedOrUnrecognizedConfig.assert_has_calls(
            [call(key) for key in unsupportedConfiguration]
        )
