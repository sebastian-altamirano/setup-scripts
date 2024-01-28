"""Contains tests for the installation step defined in `copy_application_settings.py`."""

# pylint: disable=missing-function-docstring

from inspect import unwrap
from logging import INFO as LOGGING_LEVEL_INFO
from logging import LogRecord
from typing import List, Tuple
from unittest import TestCase
from unittest.mock import ANY, Mock, call, patch

from dotfiles.installation_steps.copy_application_settings import copyApplicationSettings
from dotfiles.type_definitions import ApplicationSettingsMapping


@patch("dotfiles.installation_steps.copy_application_settings.runWithSh")
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
        _mockRunWithSh: Mock,
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
        _mockRunWithSh: Mock,
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
        _mockRunWithSh: Mock,
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

    def testIfCompletionCommandsAreExecutedAfterTheResourceIsCopied(
        self,
        _mockGetAbsolutePath: Mock,
        _mockIsAbsolutePath: Mock,
        _mockJoinPaths: Mock,
        _mockDotfilesSettingsFilePath: Mock,
        mockCopyConfiguration: Mock,
        mockRunWithSh: Mock,
    ) -> None:
        mocksManager = Mock()
        mocksManager.attach_mock(mockCopyConfiguration, "mockCopyConfiguration")
        mocksManager.attach_mock(mockRunWithSh, "mockRunWithSh")
        settingMapping: ApplicationSettingsMapping = {
            "resourceName": "fish",
            "destination": "~/.config/fish",
            "completionCommands": [["echo", "Hello"], ["echo", "Bye"]],
        }
        anotherSettingsMapping: ApplicationSettingsMapping = {
            "resourceName": ".bash_profile",
            "destination": "~/.bash_profile",
            "completionCommands": [["echo", "Hello again"]],
        }
        settingsMappings: List[ApplicationSettingsMapping] = [
            settingMapping,
            anotherSettingsMapping,
        ]

        with self.assertLogs(level=LOGGING_LEVEL_INFO) as loggerSpy:
            copyApplicationSettings(settingsMappings)

        self.assertEqual(
            [
                call.mockCopyConfiguration(settingMapping["resourceName"], ANY),
                call.mockRunWithSh(*settingMapping["completionCommands"][0]),
                call.mockRunWithSh(*settingMapping["completionCommands"][1]),
                call.mockCopyConfiguration(anotherSettingsMapping["resourceName"], ANY),
                call.mockRunWithSh(*anotherSettingsMapping["completionCommands"][0]),
            ],
            mocksManager.mock_calls,
        )
        self.assertEqual(
            len([mapping for mapping in settingsMappings if "completionCommands" in mapping]),
            len(
                [
                    record.getMessage()
                    for record in loggerSpy.records
                    if record.getMessage() == "Running completion commands..."
                ]
            ),
        )

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

    def testIfCompletionCommandsAndPostInstallationInstructionsAreOptional(
        self,
        _mockGetAbsolutePath: Mock,
        _mockIsAbsolutePath: Mock,
        _mockJoinPaths: Mock,
        _mockDotfilesSettingsFilePath: Mock,
        _mockCopyConfiguration: Mock,
        mockRunWithSh: Mock,
    ) -> None:
        settingsMapping: List[ApplicationSettingsMapping] = [
            {
                "resourceName": "fish",
                "destination": "~/.config/fish",
            }
        ]

        postInstallationInstructions = copyApplicationSettings(settingsMapping)

        mockRunWithSh.assert_not_called()
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
