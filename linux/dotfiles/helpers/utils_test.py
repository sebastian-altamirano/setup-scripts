# pylint: disable=C0116

"""Contains tests for the functions defined in `utils.py`."""

from logging import ERROR as LOGGING_LEVEL_ERROR
from logging import INFO as LOGGING_LEVEL_INFO
from logging import LogRecord
from typing import Any, Callable, List
from unittest import TestCase
from unittest.mock import Mock, patch

from dotfiles.helpers.constants import COLOR_TERMINATOR, GREEN_BG_BLACK_FG, YELLOW_BG_BLACK_FG
from dotfiles.helpers.utils import (
    installationStep,
    logCompletionMessage,
    runWithFish,
    warnAboutUnsupportedConfig,
)


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
            raise Exception("Installation step failed.")

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


@patch("dotfiles.helpers.utils.run")
class RunWithFishTests(TestCase):
    """Contains tests for the `runWithFish`function."""

    def testIfCommandIsExecutedWithFish(self, mockRun: Mock) -> None:
        args = ["echo", "Hello World!"]

        runWithFish(*args)

        mockRun.assert_called_with(["fish", "-c", *args], check=True)


class WarnAboutUnsupportedConfigTests(TestCase):
    """Contains tests for the `warnAboutUnsupportedConfig`function."""

    @patch("dotfiles.helpers.utils.warn")
    def testIfAWarningIsIssued(self, mockWarn: Mock) -> None:
        key = "quickAccessFolders"

        warnAboutUnsupportedConfig(key)

        mockWarn.assert_called_once_with(
            f'{YELLOW_BG_BLACK_FG}Configuration contains a value for "{key}", but this key is not '
            f"supported for this OS.{COLOR_TERMINATOR}"
        )

    def testIfKeyCannotBeAnEmptyString(self) -> None:
        key = ""

        with self.assertRaisesRegex(ValueError, "`key` cannot be an empty string."):
            warnAboutUnsupportedConfig(key)
