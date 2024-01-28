"""Contains tests for the decorator defined in `installation_step.py`."""

# pylint: disable=missing-function-docstring

from logging import ERROR as LOGGING_LEVEL_ERROR
from logging import INFO as LOGGING_LEVEL_INFO
from logging import LogRecord
from typing import Any, Callable
from unittest import TestCase
from unittest.mock import Mock

from dotfiles.helpers.decorators.installation_step import installationStep


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
