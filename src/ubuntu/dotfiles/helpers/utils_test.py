"""Contains tests for the functions defined in `utils.py`."""

# pylint: disable=missing-function-docstring

from abc import ABC, abstractmethod
from logging import ERROR as LOGGING_LEVEL_ERROR
from logging import INFO as LOGGING_LEVEL_INFO
from logging import LogRecord
from subprocess import CompletedProcess
from typing import Any, Callable, List, Optional, cast
from unittest import TestCase
from unittest.mock import ANY, Mock, call, patch

from dotfiles.helpers.utils import (
    copyConfiguration,
    createOrUpdateFile,
    formatConfigurationBlocks,
    getAbsolutePath,
    installationStep,
    isAbsolutePath,
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
        def getRunFunction(self) -> Callable[..., "CompletedProcess[str]"]:
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
                capture_output=True,
                check=True,
                input=None,
                text=True,
            )

        def testIfCommandIsExecutedWithPipedInput(self, mockRun: Mock) -> None:
            args = ["wc", "--chars"]
            pipedInput = "Hello World!"

            self.getRunFunction()(*args, pipedInput=pipedInput)

            mockRun.assert_called_once_with(
                self.getFinalArgs(*args),
                capture_output=True,
                check=True,
                input=pipedInput,
                text=True,
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
                    call.mockRun(ANY, capture_output=True, check=True, input=None, text=True),
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
@patch("dotfiles.helpers.utils.joinPaths")
class CopyConfigurationTests(TestCase):
    """Contains tests for the `copyConfiguration` function."""

    def testIfFileIsCopied(  # pylint: disable=too-many-arguments
        self,
        mockJoinPaths: Mock,
        mockGetAbsolutePath: Mock,
        mockPathExists: Mock,
        mockIsDirectory: Mock,
        mockCopyDirectory: Mock,
        mockCreateDirectories: Mock,
        mockCopyFile: Mock,
    ) -> None:
        fileName = ".gitconfig"
        absoluteSourcePath = f"/home/sebastian/GitHub/dotfiles/config/ubuntu/{fileName}"
        mockJoinPaths.return_value = absoluteSourcePath
        destinationPath = "~/.gitconfig"
        absoluteDestinationPath = f"/home/sebastian/{destinationPath[2:]}"
        mockGetAbsolutePath.return_value = absoluteDestinationPath
        mockPathExists.return_value = True
        mockIsDirectory.return_value = False
        mocksManager = Mock()
        mocksManager.attach_mock(mockCreateDirectories, "mockCreateDirectories")
        mocksManager.attach_mock(mockCopyFile, "mockCopyFile")

        copyConfiguration(fileName, destinationPath)

        mockCopyDirectory.assert_not_called()
        self.assertEqual(
            [
                call.mockCreateDirectories(absoluteDestinationPath, exist_ok=True),
                call.mockCopyFile(src=absoluteSourcePath, dst=absoluteDestinationPath),
            ],
            mocksManager.mock_calls,
        )

    def testIfDirectoryIsCopied(  # pylint: disable=too-many-arguments
        self,
        mockJoinPaths: Mock,
        mockGetAbsolutePath: Mock,
        mockPathExists: Mock,
        mockIsDirectory: Mock,
        mockCopyDirectory: Mock,
        mockCreateDirectories: Mock,
        mockCopyFile: Mock,
    ) -> None:
        directoryName = "fish"
        absoluteSourcePath = f"/home/sebastian/GitHub/dotfiles/config/ubuntu/{directoryName}"
        mockJoinPaths.return_value = absoluteSourcePath
        destinationPath = "~/.config/fish"
        absoluteDestinationPath = f"/home/sebastian/{destinationPath[2:]}"
        mockGetAbsolutePath.return_value = absoluteDestinationPath
        mockPathExists.return_value = True
        mockIsDirectory.return_value = True

        copyConfiguration(directoryName, destinationPath)

        mockCreateDirectories.assert_not_called()
        mockCopyFile.assert_not_called()
        mockCopyDirectory.assert_called_once_with(
            src=absoluteSourcePath, dst=absoluteDestinationPath, dirs_exist_ok=True
        )

    def testIfResourceCannotBeANonExistentResource(
        self,
        _mockJoinPaths: Mock,
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


@patch("dotfiles.helpers.utils.createDirectories")
@patch("dotfiles.helpers.utils.open")
@patch("dotfiles.helpers.utils.pathExists")
@patch("dotfiles.helpers.utils.getAbsolutePath")
class CreateOrUpdateFileTests(TestCase):
    """Contains tests for the `createOrUpdateFile` function."""

    def setUp(self) -> None:
        self.filePath = "~/.config/fish/config.fish"
        self.fileContent = "set -gx GPG_TTY (tty)"

    def testIfFileIsCreated(
        self,
        mockGetAbsolutePath: Mock,
        mockPathExists: Mock,
        mockFileOpen: Mock,
        mockCreateDirectories: Mock,
    ) -> None:
        mockPathExists.return_value = False
        mocksManager = self._getMocksManager(
            mockGetAbsolutePath, mockPathExists, mockFileOpen, mockCreateDirectories
        )

        createOrUpdateFile(self.filePath, self.fileContent)

        self.assertEqual(
            [
                call.mockGetAbsolutePath(self.filePath),
                call.mockPathExists(mockGetAbsolutePath.return_value),
                call.mockCreateDirectories(mockGetAbsolutePath.return_value, exist_ok=True),
                call.mockFileWrite(self.fileContent),
                call.mockFileWrite("\n"),
            ],
            mocksManager.mock_calls,
        )
        mockFileOpen.assert_called_once_with(
            mockGetAbsolutePath.return_value, mode="w", encoding="utf-8"
        )

    def testIfEmptyFileIsUpdated(
        self,
        mockGetAbsolutePath: Mock,
        mockPathExists: Mock,
        mockFileOpen: Mock,
        mockCreateDirectories: Mock,
    ) -> None:
        mockFileRead = self._getMockFileRead(mockFileOpen)
        mockFileRead.return_value = ""
        expectedFileWriteCalls = [
            call.mockFileWrite(self.fileContent),
            call.mockFileWrite("\n"),
        ]

        self._assertFileIsUpdated(
            mockGetAbsolutePath,
            mockPathExists,
            mockFileOpen,
            mockCreateDirectories,
            expectedFileWriteCalls,
        )

    def testIfFileThatEndsWithNewlineIsUpdated(
        self,
        mockGetAbsolutePath: Mock,
        mockPathExists: Mock,
        mockFileOpen: Mock,
        mockCreateDirectories: Mock,
    ) -> None:
        mockFileRead = self._getMockFileRead(mockFileOpen)
        mockFileRead.return_value = "eval $(ssh-agent -c)\n"
        expectedFileWriteCalls = [
            call.mockFileWrite(self.fileContent),
            call.mockFileWrite("\n"),
        ]

        self._assertFileIsUpdated(
            mockGetAbsolutePath,
            mockPathExists,
            mockFileOpen,
            mockCreateDirectories,
            expectedFileWriteCalls,
        )

    def testIfFileThatDoesNotEndWithNewlineIsUpdated(
        self,
        mockGetAbsolutePath: Mock,
        mockPathExists: Mock,
        mockFileOpen: Mock,
        mockCreateDirectories: Mock,
    ) -> None:
        mockFileRead = self._getMockFileRead(mockFileOpen)
        mockFileRead.return_value = "eval $(ssh-agent -c)"
        expectedFileWriteCalls = [
            call.mockFileWrite("\n"),
            call.mockFileWrite(self.fileContent),
            call.mockFileWrite("\n"),
        ]

        self._assertFileIsUpdated(
            mockGetAbsolutePath,
            mockPathExists,
            mockFileOpen,
            mockCreateDirectories,
            expectedFileWriteCalls,
        )

    def testIfNewlineIsNotAddedWhenContentAlreadyEndsWithIt(
        self,
        mockGetAbsolutePath: Mock,
        mockPathExists: Mock,
        mockFileOpen: Mock,
        mockCreateDirectories: Mock,
    ) -> None:
        self.fileContent = "set -gx GPG_TTY (tty)\n"
        mockFileRead = self._getMockFileRead(mockFileOpen)
        mockFileRead.return_value = ""
        expectedFileWriteCalls = [call.mockFileWrite(self.fileContent)]

        self._assertFileIsUpdated(
            mockGetAbsolutePath,
            mockPathExists,
            mockFileOpen,
            mockCreateDirectories,
            expectedFileWriteCalls,
        )

    def _assertFileIsUpdated(  # pylint: disable=too-many-arguments
        self,
        mockGetAbsolutePath: Mock,
        mockPathExists: Mock,
        mockFileOpen: Mock,
        mockCreateDirectories: Mock,
        expectedFileWriteCalls: List[Any],
    ) -> None:
        mockPathExists.return_value = True
        mocksManager = self._getMocksManager(
            mockGetAbsolutePath, mockPathExists, mockFileOpen, mockCreateDirectories
        )

        createOrUpdateFile(self.filePath, self.fileContent)

        self.assertEqual(
            [
                call.mockGetAbsolutePath(self.filePath),
                call.mockPathExists(mockGetAbsolutePath.return_value),
                *expectedFileWriteCalls,
            ],
            mocksManager.mock_calls,
        )
        mockFileOpen.assert_called_once_with(
            mockGetAbsolutePath.return_value, mode="r+", encoding="utf-8"
        )

    @staticmethod
    def _getMockFileRead(mockFileOpen: Mock) -> Mock:
        return cast(Mock, mockFileOpen.return_value.__enter__.return_value.read)

    @staticmethod
    def _getMocksManager(
        mockGetAbsolutePath: Mock,
        mockPathExists: Mock,
        mockFileOpen: Mock,
        mockCreateDirectories: Mock,
    ) -> Mock:
        mocksManager = Mock()
        mocksManager.attach_mock(mockGetAbsolutePath, "mockGetAbsolutePath")
        mocksManager.attach_mock(mockCreateDirectories, "mockCreateDirectories")
        mocksManager.attach_mock(
            mockFileOpen.return_value.__enter__.return_value.write, "mockFileWrite"
        )
        mocksManager.attach_mock(mockPathExists, "mockPathExists")
        return mocksManager


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


@patch("dotfiles.helpers.utils.absolutePath")
@patch("dotfiles.helpers.utils.expandUser")
@patch("dotfiles.helpers.utils.expandVars")
class GetAbsolutePathTests(TestCase):
    """Contains tests for the `getAbsolutePath` function."""

    def testIfAbsolutePathIsReturned(
        self, _mockExpandVars: Mock, _mockExpandUser: Mock, mockAbsolutePath: Mock
    ) -> None:
        filePath = "~/GitHub/dotfiles/config/settings.json"

        absoluteFilePath = getAbsolutePath(filePath)

        self.assertEqual(mockAbsolutePath.return_value, absoluteFilePath)
        mockAbsolutePath.assert_called_once()

    def testIfUserHomeAndEnvironmentVariablesAreExpanded(
        self, mockExpandVars: Mock, mockExpandUser: Mock, mockAbsolutePath: Mock
    ) -> None:
        filePath = "~/GitHub/dotfiles/config/settings.json"

        getAbsolutePath(filePath)

        mockExpandVars.assert_called_once_with(filePath)
        mockExpandUser.assert_called_once_with(mockExpandVars.return_value)
        mockAbsolutePath.assert_called_once_with(mockExpandUser.return_value)


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


@patch("dotfiles.helpers.utils.isAbsolute")
@patch("dotfiles.helpers.utils.expandUser")
@patch("dotfiles.helpers.utils.expandVars")
class IsAbsolutePathTests(TestCase):
    """Contains tests for the `isAbsolutePath` function."""

    def testIfTheCheckIsPerformed(
        self, _mockExpandVars: Mock, _mockExpandUser: Mock, mockIsAbsolute: Mock
    ) -> None:
        filePath = "~/GitHub/dotfiles/config/settings.json"

        absoluteFilePath = isAbsolutePath(filePath)

        self.assertEqual(mockIsAbsolute.return_value, absoluteFilePath)
        mockIsAbsolute.assert_called_once()

    def testIfUserHomeAndEnvironmentVariablesAreExpanded(
        self, mockExpandVars: Mock, mockExpandUser: Mock, mockIsAbsolute: Mock
    ) -> None:
        filePath = "~/GitHub/dotfiles/config/settings.json"

        isAbsolutePath(filePath)

        mockExpandVars.assert_called_once_with(filePath)
        mockExpandUser.assert_called_once_with(mockExpandVars.return_value)
        mockIsAbsolute.assert_called_once_with(mockExpandUser.return_value)


class LogCompletionMessageTests(TestCase):
    """Contains tests for the `logCompletionMessage` function."""

    def testIfCompletionMessageIsLogged(self) -> None:
        greenBackgroundBlackForeground = "\x1b[6;30;42m"
        colorTerminator = "\x1b[0m"

        with self.assertLogs() as loggerSpy:
            logCompletionMessage()

            self.assertEqual(1, len(loggerSpy.records))
            self.assertEqual(LOGGING_LEVEL_INFO, loggerSpy.records[0].levelno)
            self.assertEqual(
                f"{greenBackgroundBlackForeground}Finished!{colorTerminator}",
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

    def getRunFunction(self) -> Callable[..., "CompletedProcess[str]"]:
        return runWithFish


class RunWithShTests(BaseTests.RunWithBaseTests):
    """Contains tests for the `runWithSh`function."""

    def getRunFunction(self) -> Callable[..., "CompletedProcess[str]"]:
        return runWithSh


class WarnAboutUnsupportedOrUnrecognizedConfigTests(TestCase):
    """Contains tests for the `warnAboutUnsupportedOrUnrecognizedConfig`function."""

    @patch("dotfiles.helpers.utils.warn")
    def testIfAWarningIsIssued(self, mockWarn: Mock) -> None:
        yellowBackgroundBlackForeground = "\x1b[6;30;43m"
        colorTerminator = "\x1b[0m"
        key = "quickAccessFolders"

        warnAboutUnsupportedOrUnrecognizedConfig(key)

        mockWarn.assert_called_once_with(
            f'{yellowBackgroundBlackForeground}The configuration contains a value for "{key}", but '
            f"this key is either not recognized or is not supported by this OS.{colorTerminator}"
        )

    def testIfKeyCannotBeAnEmptyString(self) -> None:
        key = ""

        with self.assertRaisesRegex(ValueError, "`key` cannot be an empty string."):
            warnAboutUnsupportedOrUnrecognizedConfig(key)
