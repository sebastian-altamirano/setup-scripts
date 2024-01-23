"""Contains tests for the functions defined in `install.py`."""

# pylint: disable=missing-function-docstring

from unittest import TestCase
from unittest.mock import Mock, call, patch

from dotfiles.install import install
from dotfiles.type_definitions import Config


@patch("dotfiles.install.warnAboutUnsupportedOrUnrecognizedConfig")
@patch("dotfiles.install.logCompletionMessage")
@patch("dotfiles.install.readJson")
@patch("dotfiles.install.Path")
@patch("dotfiles.install.DOTFILES_SETTINGS_FILE_PATH")
@patch("dotfiles.install.installationSteps")
class InstallTests(TestCase):
    """Contains tests for the `install` function."""

    def testIfAllConfigurationKeysAreOptional(  # pylint: disable=too-many-arguments
        self,
        mockInstallationSteps: Mock,
        _mockDotfilesSettingsFilePath: Mock,
        _mockPath: Mock,
        mockReadJson: Mock,
        mockLogCompletionMessage: Mock,
        mockWarnAboutUnsupportedOrUnrecognizedConfig: Mock,
    ) -> None:
        emptyConfiguration: Config = {}
        mockReadJson.return_value = emptyConfiguration

        install()

        mockInstallationSteps.installFish.assert_called()
        mockInstallationSteps.upgradeSystemDependencies.assert_called()
        mockInstallationSteps.installPackages.assert_called()
        mockWarnAboutUnsupportedOrUnrecognizedConfig.assert_not_called()
        mockInstallationSteps.installVSCodeExtensions.assert_not_called()
        mockInstallationSteps.copyApplicationSettings.assert_not_called()
        mockLogCompletionMessage.assert_called()

    def testIfPostInstallationInstructionAreCollectedAndDisplayed(
        self,
        mockInstallationSteps: Mock,
        _mockDotfilesSettingsFilePath: Mock,
        _mockPath: Mock,
        mockReadJson: Mock,
        mockLogCompletionMessage: Mock,
        _mockWarnAboutUnsupportedOrUnrecognizedConfig: Mock,
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
        _mockInstallationSteps: Mock,
        _mockDotfilesSettingsFilePath: Mock,
        _mockPath: Mock,
        mockReadJson: Mock,
        _mockLogCompletionMessage: Mock,
        mockWarnAboutUnsupportedOrUnrecognizedConfig: Mock,
    ) -> None:
        unsupportedConfiguration = {"unsupportedConfigurationKey": "Unsupported configuration"}
        mockReadJson.return_value = unsupportedConfiguration

        install()

        mockWarnAboutUnsupportedOrUnrecognizedConfig.assert_has_calls(
            [call(key) for key in unsupportedConfiguration]
        )
