"""Contains tests for the utils defined in `run_with.py`."""

# pylint: disable=missing-function-docstring

from abc import ABC, abstractmethod
from subprocess import CompletedProcess
from typing import Callable, List, Optional
from unittest import TestCase
from unittest.mock import ANY, Mock, call, patch

from dotfiles.helpers.utils.run_with import runWithFish, runWithSh


class BaseTests:  # pylint: disable=too-few-public-methods
    """Contains base test classes."""

    @patch("dotfiles.helpers.utils.run_with.run")
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

        @patch("dotfiles.helpers.utils.run_with.logInfo")
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
