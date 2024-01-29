"""Contains tests for the installation step defined in `copy_application_settings.py`."""

# pylint: disable=missing-function-docstring

from inspect import unwrap
from logging import INFO as LOGGING_LEVEL_INFO
from logging import LogRecord
from typing import List, Tuple
from unittest import TestCase
from unittest.mock import Mock, patch

from dotfiles.installation_steps.copy_application_settings import copyApplicationSettings
from dotfiles.type_definitions import ApplicationSettingsMapping


@patch("dotfiles.installation_steps.copy_application_settings.copyConfiguration")
@patch("dotfiles.installation_steps.copy_application_settings.DOTFILES_SETTINGS_FILE_PATH")
@patch("dotfiles.installation_steps.copy_application_settings.joinPaths")
@patch("dotfiles.installation_steps.copy_application_settings.isAbsolutePath")
@patch("dotfiles.installation_steps.copy_application_settings.getAbsolutePath")
class CopyApplicationSettingsTests(TestCase):
    """Contains tests for the `copyApplicationSettings` function."""

    def testIfAbsoluteDestinationPathIsCalculatedRelativeToTheSettingsFile(  # pylint: disable=too-many-arguments
        self,
        mockGetAbsolutePath: Mock,
        mockIsAbsolutePath: Mock,
        mockJoinPaths: Mock,
        mockDotfilesSettingsFilePath: Mock,
        mockCopyConfiguration: Mock,
    ) -> None:
        settingsMapping: ApplicationSettingsMapping = {
            "resourceName": "fish",
            "destination": "../.config/fish",
        }
        mockIsAbsolutePath.return_value = False

        copyApplicationSettings([settingsMapping])

        mockJoinPaths.assert_called_once_with(
            mockDotfilesSettingsFilePath, settingsMapping["destination"]
        )
        mockGetAbsolutePath.assert_called_once_with(mockJoinPaths.return_value)
        mockCopyConfiguration.assert_called_once_with(
            settingsMapping["resourceName"], mockGetAbsolutePath.return_value
        )

    def testIfResourceIsCopied(
        self,
        mockGetAbsolutePath: Mock,
        _mockIsAbsolutePath: Mock,
        _mockJoinPaths: Mock,
        _mockDotfilesSettingsFilePath: Mock,
        mockCopyConfiguration: Mock,
    ) -> None:
        settingsMapping: ApplicationSettingsMapping = {
            "resourceName": "fish",
            "destination": "~/.config/fish",
        }

        copyApplicationSettings([settingsMapping])

        mockCopyConfiguration.assert_called_once_with(
            settingsMapping["resourceName"], mockGetAbsolutePath.return_value
        )

    def testIfAllResourcesAreCopied(
        self,
        _mockGetAbsolutePath: Mock,
        _mockIsAbsolutePath: Mock,
        _mockJoinPaths: Mock,
        _mockDotfilesSettingsFilePath: Mock,
        mockCopyConfiguration: Mock,
    ) -> None:
        settingsMappings: List[ApplicationSettingsMapping] = [
            {
                "resourceName": "fish",
                "destination": "~/.config/fish",
            },
            {"resourceName": ".bash_profile", "destination": "~/.bash_profile"},
        ]

        copyApplicationSettings(settingsMappings)

        self.assertEqual(len(settingsMappings), mockCopyConfiguration.call_count)

    def testIfPostInstallationInstructionsAreReturned(self, *_args: Tuple[Mock, Mock]) -> None:
        settingMapping: ApplicationSettingsMapping = {
            "resourceName": "fish",
            "destination": "~/.config/fish",
            "postInstallationInstructions": (
                "This is where I would put my post-installation instructions, if I had any!"
            ),
        }
        anotherSettingsMapping: ApplicationSettingsMapping = {
            "resourceName": ".bash_profile",
            "destination": "~/.bash_profile",
            "postInstallationInstructions": "There is nothing else to do...",
        }
        settingMappings = [settingMapping, anotherSettingsMapping]
        expectedPostInstallationInstructions: List[str] = [
            settingMapping["postInstallationInstructions"],
            anotherSettingsMapping["postInstallationInstructions"],
        ]

        postInstallationInstructions = copyApplicationSettings(settingMappings)

        self.assertEqual(expectedPostInstallationInstructions, postInstallationInstructions)

    def testIfPostInstallationInstructionsAreOptional(
        self,
        _mockGetAbsolutePath: Mock,
        _mockIsAbsolutePath: Mock,
        _mockJoinPaths: Mock,
        _mockDotfilesSettingsFilePath: Mock,
        _mockCopyConfiguration: Mock,
    ) -> None:
        settingsMapping: List[ApplicationSettingsMapping] = [
            {
                "resourceName": "fish",
                "destination": "~/.config/fish",
            }
        ]

        postInstallationInstructions = copyApplicationSettings(settingsMapping)

        self.assertEqual([], postInstallationInstructions)

    def testIfTheResourcesAreLoggedAsTheyAreCopied(
        self, mockGetAbsolutePath: Mock, *_args: Tuple[Mock, Mock]
    ) -> None:
        settingsMappings: List[ApplicationSettingsMapping] = [
            {
                "resourceName": "fish",
                "destination": "~/.config/fish",
            },
            {"resourceName": ".bash_profile", "destination": "~/.bash_profile"},
        ]

        def getAbsolutePathSideEffect(path: str) -> str:
            return path

        mockGetAbsolutePath.side_effect = getAbsolutePathSideEffect

        with self.assertLogs(level=LOGGING_LEVEL_INFO) as loggerSpy:
            unwrap(copyApplicationSettings)(settingsMappings)

        self.assertEqual(2, len(loggerSpy.records))
        self._assertResourceCopyLog(loggerSpy.records[0], settingsMappings[0])
        self._assertResourceCopyLog(loggerSpy.records[1], settingsMappings[1])

    def _assertResourceCopyLog(
        self, logRecord: LogRecord, settingsMapping: ApplicationSettingsMapping
    ) -> None:
        self.assertEqual(
            f'Copying "{settingsMapping["resourceName"]}" to "{settingsMapping["destination"]}"...',
            logRecord.getMessage(),
        )
