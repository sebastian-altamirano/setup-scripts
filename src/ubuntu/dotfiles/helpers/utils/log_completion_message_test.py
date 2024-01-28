"""Contains tests for the util defined in `log_completion_message.py`."""

# pylint: disable=missing-function-docstring

from logging import INFO as LOGGING_LEVEL_INFO
from logging import LogRecord
from typing import List
from unittest import TestCase

from dotfiles.helpers.utils.log_completion_message import logCompletionMessage


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
