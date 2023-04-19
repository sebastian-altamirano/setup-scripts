# pylint: disable=C0116

"""Contains tests for the functions defined in `installation_steps.py`."""

from ast import FunctionDef
from ast import Name as AstName
from ast import parse as parseAst
from inspect import getsource as getSource
from inspect import unwrap
from logging import ERROR as LOGGING_LEVEL_ERROR
from logging import INFO as LOGGING_LEVEL_INFO
from logging import LogRecord
from typing import Any, List, Tuple
from unittest import TestCase
from unittest.mock import ANY, Mock, call, patch

import dotfiles.installation_steps as installationSteps
from dotfiles.helpers.utils import installationStep
from dotfiles.installation_steps import copyApplicationSettings, installVSCodeExtensions
from dotfiles.type_definitions import ApplicationSettingsMapping


@patch("dotfiles.helpers.installation_steps.run")
@patch("dotfiles.helpers.installation_steps.copyFile")
@patch("dotfiles.helpers.installation_steps.getAbsolutePath")
@patch("dotfiles.helpers.installation_steps.createDirectories")
@patch("dotfiles.helpers.installation_steps.isAbsolutePath", return_value=True)
class CopyApplicationSettingsTests(TestCase):
    """Contains tests for the `copyApplicationSettings` function."""

    def testIfResourceIsCopied(
        self,
        mockIsAbsolutePath: Mock,
        mockCreateDirectories: Mock,
        mockGetAbsolutePath: Mock,
        mockCopyFile: Mock,
        _mockRun: Mock,
    ) -> None:
        mocksManager = Mock()
        mocksManager.attach_mock(mockIsAbsolutePath, "mockIsAbsolutePath")
        mocksManager.attach_mock(mockCreateDirectories, "mockCreateDirectories")
        mocksManager.attach_mock(mockGetAbsolutePath, "mockGetAbsolutePath")
        mocksManager.attach_mock(mockCopyFile, "mockCopyFile")
        settingsMapping: ApplicationSettingsMapping = {
            "resourceName": "fish",
            "destination": "~/.config/fish",
        }

        copyApplicationSettings([settingsMapping])

        self.assertEqual(
            [
                call.mockIsAbsolutePath(settingsMapping["destination"]),
                call.mockCreateDirectories(settingsMapping["destination"], exist_ok=True),
                call.mockGetAbsolutePath(f"app-settings/{settingsMapping['resourceName']}"),
                call.mockCopyFile(
                    src=mockGetAbsolutePath.return_value, dst=settingsMapping["destination"]
                ),
            ],
            mocksManager.mock_calls,
        )

    def testIfAllResourcesAreCopied(
        self,
        _mockIsAbsolutePath: Mock,
        _mockCreateDirectories: Mock,
        _mockGetAbsolutePath: Mock,
        mockCopyFile: Mock,
        _mockRun: Mock,
    ) -> None:
        settingsMappings: List[ApplicationSettingsMapping] = [
            {
                "resourceName": "fish",
                "destination": "~/.config/fish",
            },
            {"resourceName": ".gitconfig", "destination": "~/.gitconfig"},
        ]

        copyApplicationSettings(settingsMappings)

        self.assertEqual(len(settingsMappings), mockCopyFile.call_count)

    def testIfCompletionCommandsAreExecutedAfterTheResourceIsCopied(
        self,
        _mockIsAbsolutePath: Mock,
        _mockCreateDirectories: Mock,
        _mockGetAbsolutePath: Mock,
        mockCopyFile: Mock,
        mockRun: Mock,
    ) -> None:
        mocksManager = Mock()
        mocksManager.attach_mock(mockCopyFile, "mockCopyFile")
        mocksManager.attach_mock(mockRun, "mockRun")
        settingMapping: ApplicationSettingsMapping = {
            "resourceName": "fish",
            "destination": "~/.config/fish",
            "completionCommands": [["echo", "Hello"], ["echo", "Bye"]],
        }
        anotherSettingsMapping: ApplicationSettingsMapping = {
            "resourceName": ".gitconfig",
            "destination": "~/.gitconfig",
            "completionCommands": [["echo", "Hello again"]],
        }
        settingsMappings: List[ApplicationSettingsMapping] = [
            settingMapping,
            anotherSettingsMapping,
        ]

        copyApplicationSettings(settingsMappings)

        self.assertEqual(
            [
                call.mockCopyFile(src=ANY, dst=settingMapping["destination"]),
                call.mockRun(settingMapping["completionCommands"][0], check=True),
                call.mockRun(settingMapping["completionCommands"][1], check=True),
                call.mockCopyFile(src=ANY, dst=anotherSettingsMapping["destination"]),
                call.mockRun(anotherSettingsMapping["completionCommands"][0], check=True),
            ],
            mocksManager.mock_calls,
        )

    def testIfPostInstallationInstructionsAreReturned(
        self, *_args: Tuple[Mock, Mock, Mock, Mock, Mock]
    ) -> None:
        settingMapping: ApplicationSettingsMapping = {
            "resourceName": "fish",
            "destination": "~/.config/fish",
            "postInstallationInstructions": (
                "This is where I would put my post-installation instructions, if I had any!"
            ),
        }
        anotherSettingsMapping: ApplicationSettingsMapping = {
            "resourceName": ".gitconfig",
            "destination": "~/.gitconfig",
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
        _mockIsAbsolutePath: Mock,
        _mockCreateDirectories: Mock,
        _mockGetAbsolutePath: Mock,
        _mockCopyFile: Mock,
        mockRun: Mock,
    ) -> None:
        settingsMapping: List[ApplicationSettingsMapping] = [
            {
                "resourceName": "fish",
                "destination": "~/.config/fish",
            }
        ]

        postInstallationInstructions = copyApplicationSettings(settingsMapping)

        mockRun.assert_not_called()
        self.assertEqual([], postInstallationInstructions)

    def testIfAMappingWithARelativeDestinationIsIgnored(
        self,
        mockIsAbsolutePath: Mock,
        _mockCreateDirectories: Mock,
        _mockGetAbsolutePath: Mock,
        mockCopyFile: Mock,
        _mockRun: Mock,
    ) -> None:
        invalidSettingsMapping: ApplicationSettingsMapping = {
            "resourceName": "fish",
            "destination": "./.config/fish",
        }
        validSettingsMapping: ApplicationSettingsMapping = {
            "resourceName": ".gitconfig",
            "destination": "~/.gitconfig",
        }

        def isAbsolutePath(path: str) -> bool:
            return path == validSettingsMapping["destination"]

        mockIsAbsolutePath.side_effect = isAbsolutePath
        settingMappings = [invalidSettingsMapping, validSettingsMapping]

        with self.assertLogs(level=LOGGING_LEVEL_ERROR) as loggerSpy:
            unwrap(copyApplicationSettings)(settingMappings)

        self.assertEqual(1, len(loggerSpy.records))
        self.assertEqual(
            f'Could not copy "{invalidSettingsMapping["resourceName"]}", an absolute path was '
            f'expected for "destination", but "{invalidSettingsMapping["destination"]}" was '
            "received.",
            loggerSpy.records[0].getMessage(),
        )
        mockCopyFile.assert_called_once_with(src=ANY, dst=validSettingsMapping["destination"])

    def testIfTheResourcesAreLoggedAsTheyAreCopied(
        self, *_args: Tuple[Mock, Mock, Mock, Mock, Mock]
    ) -> None:
        settingsMappings: List[ApplicationSettingsMapping] = [
            {
                "resourceName": "fish",
                "destination": "~/.config/fish",
            },
            {"resourceName": ".gitconfig", "destination": "~/.gitconfig"},
        ]

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


@patch("dotfiles.helpers.installation_steps.run")
class InstallVSCodeExtensionsTests(TestCase):
    """Contains tests for the `installVSCodeExtensions` function."""

    def testIfAllExtensionsAreInstalled(self, mockRun: Mock) -> None:
        mockRun.return_value.stderr = ""
        extensions = ["theme", "linter", "another-linter", "language-support"]

        with self.assertNoLogs():
            unwrap(installVSCodeExtensions)(extensions)

        mockRun.assert_has_calls(
            [
                call(["code", "--install-extension", extension], capture_output=True, check=True)
                for extension in extensions
            ],
            any_order=True,
        )

    def testIfExtensionsThatCouldNotBeInstalledAreLogged(self, mockRun: Mock) -> None:
        extensionThatExists = "extension-that-exists"
        extensionThatDoesNotExist = "extension-that-does-not-exist"
        extensions = [extensionThatExists, extensionThatDoesNotExist]

        def fillStdErrIfExtensionDoesNotExist(arguments: List[str], **kwargs: Any) -> Mock:
            return Mock(
                stderr="An error has occurred..."
                if arguments[2] == extensionThatDoesNotExist
                else ""
            )

        mockRun.side_effect = fillStdErrIfExtensionDoesNotExist

        with self.assertLogs() as loggerSpy:
            unwrap(installVSCodeExtensions)(extensions)

        self.assertEqual(1, len(loggerSpy.records))
        self.assertEqual(LOGGING_LEVEL_ERROR, loggerSpy.records[0].levelno)
        self.assertEqual(
            f"Could not install the following extensions:\n- {extensionThatDoesNotExist}\n",
            loggerSpy.records[0].getMessage(),
        )


class GeneralTests(TestCase):
    """Contains tests that apply to all installation steps."""

    def testIfAllInstallationStepsAreDecorated(self) -> None:
        abstractSintaxTree = parseAst(getSource(installationSteps))

        functionsDecorators = [
            node.decorator_list for node in abstractSintaxTree.body if isinstance(node, FunctionDef)
        ]

        for functionDecorators in functionsDecorators:
            self.assertTrue(
                any(
                    installationStep.__name__ == functionDecorator.id
                    for functionDecorator in functionDecorators
                    if isinstance(functionDecorator, AstName)
                )
            )
