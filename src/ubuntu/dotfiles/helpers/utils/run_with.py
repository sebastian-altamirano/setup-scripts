"""Defines utility functions to execute commands with different shells."""

from logging import info as logInfo
from subprocess import CompletedProcess, run
from typing import Optional


def _runWith(*args: str, pipedInput: Optional[str] = None) -> "CompletedProcess[str]":
    logInfo(*args)
    return run([*args], capture_output=True, check=True, input=pipedInput, text=True)


def runWithFish(*args: str, pipedInput: Optional[str] = None) -> "CompletedProcess[str]":
    """Runs a command with fish.

    The command is logged before being executed.

    Raises:
        CalledProcessError: If the command execution failed.
    """
    return _runWith("fish", "-c", *args, pipedInput=pipedInput)


def runWithSh(*args: str, pipedInput: Optional[str] = None) -> "CompletedProcess[str]":
    """Runs a command with sh.

    The command is logged before being executed.

    Raises:
        CalledProcessError: If the command execution failed.
    """
    return _runWith(*args, pipedInput=pipedInput)
