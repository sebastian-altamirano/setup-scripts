"""Contains tests for the functions defined in `utils.py`."""

# pylint: disable=missing-function-docstring

from abc import ABC, abstractmethod
from logging import ERROR as LOGGING_LEVEL_ERROR
from logging import INFO as LOGGING_LEVEL_INFO
from logging import LogRecord
from typing import Any, Callable, List, Optional
from unittest import TestCase
from unittest.mock import ANY, Mock, call, patch

from dotfiles.helpers.constants import COLOR_TERMINATOR, GREEN_BG_BLACK_FG, YELLOW_BG_BLACK_FG
from dotfiles.helpers.utils import (
    copyConfiguration,
    formatConfigurationBlocks,
    installationStep,
    logCompletionMessage,
    runWithFish,
    runWithSh,
    warnAboutUnsupportedOrUnrecognizedConfig,
)


class BaseTests:  # pylint: disable=too-few-public-methods
    """Contains base test classes."""

    @patch("dotfiles.helpers.utils.run")
    class RunWithBaseTests(ABC, TestCase):
        """Contains base tests for `runWith...` functions."""

        @abstractmethod
        def getRunFunction(self) -> Callable[..., None]:
            """Returns the function used to run the commands."""

        def getShell(self) -> Optional[str]:
            """Returns the shell used to run the commands."""
            return None

        def getFinalArgs(self, *args: str) -> List[str]:
            """Returns the arguments as they are passed to the run function."""
            shell = self.getShell()  # pylint: disable=assignment-from-none
            shellArgs: List[str] = [] if shell is None else [shell, "-c"]
            return [*shellArgs, *args]

        def testIfCommandIsExecuted(self, mockRun: Mock) -> None:
            args = ["echo", "Hello World!"]

            self.getRunFunction()(*args)

            mockRun.assert_called_once_with(
                self.getFinalArgs(*args),
                check=True,
            )

        @patch("dotfiles.helpers.utils.logInfo")
        def testIfCommandIsLoggedBeforeBeingExecuted(
            self, mockLogInfo: Mock, mockRun: Mock
        ) -> None:
            mocksManager = Mock()
            mocksManager.attach_mock(mockLogInfo, "mockLogInfo")
            mocksManager.attach_mock(mockRun, "mockRun")
            args = ["echo", "Hello World!"]

            self.getRunFunction()(*args)

            self.assertEqual(
                [
                    call.mockLogInfo(*self.getFinalArgs(*args)),
                    call.mockRun(ANY, check=True),
                ],
                mocksManager.mock_calls,
            )
            mockLogInfo.assert_called_once()


@patch("dotfiles.helpers.utils.copyFile")
@patch("dotfiles.helpers.utils.createDirectories")
@patch("dotfiles.helpers.utils.copyDirectory")
@patch("dotfiles.helpers.utils.isDirectory")
@patch("dotfiles.helpers.utils.pathExists")
@patch("dotfiles.helpers.utils.getAbsolutePath")
class CopyConfigurationTests(TestCase):
    """Contains tests for the `copyConfiguration` function."""

    def testIfFileIsCopied(  # pylint: disable=too-many-arguments
        self,
        mockGetAbsolutePath: Mock,
        mockPathExists: Mock,
        mockIsDirectory: Mock,
        mockCopyDirectory: Mock,
        mockCreateDirectories: Mock,
        mockCopyFile: Mock,
    ) -> None:
        fileName = ".gitconfig"
        sourcePath = f"../../../../config/ubuntu/{fileName}"
        destinationPath = "~/.gitconfig"
        mockGetAbsolutePath.side_effect = self._mockGetAbsolutePath
        mockPathExists.return_value = True
        mockIsDirectory.return_value = False
        mocksManager = Mock()
        mocksManager.attach_mock(mockCreateDirectories, "mockCreateDirectories")
        mocksManager.attach_mock(mockCopyFile, "mockCopyFile")

        copyConfiguration(fileName, destinationPath)

        mockCopyDirectory.assert_not_called()
        self.assertEqual(
            [
                call.mockCreateDirectories(f"/abs/{destinationPath}", exist_ok=True),
                call.mockCopyFile(src=f"/abs/{sourcePath}", dst=f"/abs/{destinationPath}"),
            ],
            mocksManager.mock_calls,
        )

    def testIfDirectoryIsCopied(  # pylint: disable=too-many-arguments
        self,
        mockGetAbsolutePath: Mock,
        mockPathExists: Mock,
        mockIsDirectory: Mock,
        mockCopyDirectory: Mock,
        mockCreateDirectories: Mock,
        mockCopyFile: Mock,
    ) -> None:
        dirName = "fish"
        sourcePath = f"../../../../config/ubuntu/{dirName}"
        destinationPath = "~/.config/fish"
        mockGetAbsolutePath.side_effect = self._mockGetAbsolutePath
        mockPathExists.return_value = True
        mockIsDirectory.return_value = True

        copyConfiguration(dirName, destinationPath)

        mockCreateDirectories.assert_not_called()
        mockCopyFile.assert_not_called()
        mockCopyDirectory.assert_called_once_with(
            src=f"/abs/{sourcePath}", dst=f"/abs/{destinationPath}", dirs_exist_ok=True
        )

    def testIfResourceCannotBeANonExistentResource(
        self,
        _mockGetAbsolutePath: Mock,
        mockPathExists: Mock,
        _mockIsDirectory: Mock,
        _mockCopyDirectory: Mock,
        _mockCreateDirectories: Mock,
        _mockCopyFile: Mock,
    ) -> None:
        nonExistentResource = "asdasdsa"
        destinationPath = '~/.config/fish"'
        mockPathExists.return_value = False

        with self.assertRaises(FileNotFoundError):
            copyConfiguration(nonExistentResource, destinationPath)

    @staticmethod
    def _mockGetAbsolutePath(path: str) -> str:
        return f"/abs/{path}"


class FormatConfigurationBlocksTests(TestCase):
    """Contains tests for the `formatConfigurationBlocks` function."""

    def testIfConfigurationBlocksAreFormattedCorrectly(self) -> None:
        configurationBlocks = [
            [
                "# Cache the password for 10 hours.",
                "cache-password true",
                "cache-password-time 36000",
            ],
            ["# Allow committing from VSCode.", "allow-commiting-from-vscode true"],
        ]

        formattedConfigurationBlocks = formatConfigurationBlocks(configurationBlocks)

        self.assertEqual(
            (
                f"{configurationBlocks[0][0]}\n"
                f"{configurationBlocks[0][1]}\n"
                f"{configurationBlocks[0][2]}\n\n"
                f"{configurationBlocks[1][0]}\n"
                f"{configurationBlocks[1][1]}\n"
            ),
            formattedConfigurationBlocks,
        )

    def testIfEmptyBlocksAreFilteredOut(self) -> None:
        configurationBlocks: List[List[str]] = [
            [],
            ["# Allow committing from VSCode.", "allow-commiting-from-vscode true"],
        ]

        formattedConfigurationBlocks = formatConfigurationBlocks(configurationBlocks)

        self.assertEqual(
            (f"{configurationBlocks[1][0]}\n" f"{configurationBlocks[1][1]}\n"),
            formattedConfigurationBlocks,
        )

    def testIfAnEmptyStringIsReturnedIfThereAreNoBlocks(self) -> None:
        configurationBlocks: List[List[str]] = []

        formattedConfigurationBlocks = formatConfigurationBlocks(configurationBlocks)

        self.assertEqual("", formattedConfigurationBlocks)


class InstallationStepTests(TestCase):
    """Contains tests for the `installationStep` decorator."""

    def testIfInstallationStepIsExecutedAndItsReturnValueReturned(self) -> None:
        function = Mock()
        function.__name__ = "dummyInstallationStep"
        function.return_value = 1234
        arguments = [1, 2, 3, 4]

        returnValue = installationStep(function)(*arguments)

        self.assertEqual(function.return_value, returnValue)
        function.assert_called_once_with(*arguments)

    def testIfStartAndFinishIsLogged(self) -> None:
        @installationStep
        def function() -> None:
            ...

        with self.assertLogs() as loggerSpy:
            function()

        self.assertEqual(2, len(loggerSpy.records))
        self._assertCallbackStartedLog(loggerSpy.records[0], function)
        self._assertCallbackFinishedLog(loggerSpy.records[1], function)

    def testIfStartAndErrorIsLogged(self) -> None:
        @installationStep
        def function() -> None:
            raise Exception("Installation step failed.")  # pylint: disable=broad-exception-raised

        with self.assertLogs() as loggerSpy, self.assertRaises(Exception):
            function()

        self.assertEqual(2, len(loggerSpy.records))
        self._assertCallbackStartedLog(loggerSpy.records[0], function)
        self._assertCallbackFailedLog(loggerSpy.records[1], function)

    def _assertCallbackStartedLog(self, logRecord: LogRecord, callback: Callable[..., Any]) -> None:
        self.assertEqual(f"--- Starting step: `{callback.__name__}` ---", logRecord.getMessage())
        self.assertEqual(LOGGING_LEVEL_INFO, logRecord.levelno)

    def _assertCallbackFinishedLog(
        self, logRecord: LogRecord, callback: Callable[..., Any]
    ) -> None:
        self.assertEqual(f"--- Finished step: `{callback.__name__}` ---\n", logRecord.getMessage())
        self.assertEqual(LOGGING_LEVEL_INFO, logRecord.levelno)

    def _assertCallbackFailedLog(self, logRecord: LogRecord, callback: Callable[..., Any]) -> None:
        self.assertEqual(f"--- Failed step: `{callback.__name__}` ---\n", logRecord.getMessage())
        self.assertEqual(LOGGING_LEVEL_ERROR, logRecord.levelno)
        self.assertIsNotNone(logRecord.exc_info)


class LogCompletionMessageTests(TestCase):
    """Contains tests for the `logCompletionMessage` function."""

    def testIfCompletionMessageIsLogged(self) -> None:
        with self.assertLogs() as loggerSpy:
            logCompletionMessage()

            self.assertEqual(1, len(loggerSpy.records))
            self.assertEqual(LOGGING_LEVEL_INFO, loggerSpy.records[0].levelno)
            self.assertEqual(
                f"{GREEN_BG_BLACK_FG}Finished!{COLOR_TERMINATOR}",
                loggerSpy.records[0].getMessage(),
            )

    def testIfPostInstallationInstructionsAreLogged(self) -> None:
        postInstallationInstructions: List[str] = ["do such a thing", "do such other thing"]

        with self.assertLogs() as loggerSpy:
            logCompletionMessage(postInstallationInstructions)

            self.assertEqual(4, len(loggerSpy.records))
            self.assertEqual(
                "Now there are some manual steps you need to perform:",
                loggerSpy.records[1].getMessage(),
            )
            self._assertPostInstallationInstructionLog(
                loggerSpy.records[2], postInstallationInstructions[0]
            )
            self._assertPostInstallationInstructionLog(
                loggerSpy.records[3], postInstallationInstructions[1]
            )

    def _assertPostInstallationInstructionLog(
        self, logRecord: LogRecord, postInstallationInstruction: str
    ) -> None:
        self.assertEqual(LOGGING_LEVEL_INFO, logRecord.levelno)
        self.assertEqual(f"- {postInstallationInstruction}", logRecord.getMessage())


class RunWithFishTests(BaseTests.RunWithBaseTests):
    """Contains tests for the `runWithFish`function."""

    def getShell(self) -> Optional[str]:
        return "fish"

    def getRunFunction(self) -> Callable[..., None]:
        return runWithFish


class RunWithShTests(BaseTests.RunWithBaseTests):
    """Contains tests for the `runWithSh`function."""

    def getRunFunction(self) -> Callable[..., None]:
        return runWithSh


class WarnAboutUnsupportedOrUnrecognizedConfigTests(TestCase):
    """Contains tests for the `warnAboutUnsupportedOrUnrecognizedConfig`function."""

    @patch("dotfiles.helpers.utils.warn")
    def testIfAWarningIsIssued(self, mockWarn: Mock) -> None:
        key = "quickAccessFolders"

        warnAboutUnsupportedOrUnrecognizedConfig(key)

        mockWarn.assert_called_once_with(
            f'{YELLOW_BG_BLACK_FG}The configuration contains a value for "{key}", but this key is '
            f"either not recognized or is not supported by this OS.{COLOR_TERMINATOR}"
        )

    def testIfKeyCannotBeAnEmptyString(self) -> None:
        key = ""

        with self.assertRaisesRegex(ValueError, "`key` cannot be an empty string."):
            warnAboutUnsupportedOrUnrecognizedConfig(key)
