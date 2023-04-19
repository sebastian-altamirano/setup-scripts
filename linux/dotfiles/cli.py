"""Defines the aplication entry point."""

from argparse import ArgumentParser
from logging import INFO as LOGGING_LEVEL_INFO
from logging import FileHandler, StreamHandler
from logging import basicConfig as configureLogging
from logging import captureWarnings as logWarnings
from logging import exception as logException
from os.path import abspath as getAbsolutePath
from pathlib import Path
from sys import argv
from typing import Optional, Sequence, cast

from dotfiles import __version__
from dotfiles.install import install
from dotfiles.type_definitions import Arguments


def _parseArguments(arguments: Optional[Sequence[str]] = None) -> Arguments:
    parser = ArgumentParser(description="Installation script for Linux dotfiles.")
    parser.add_argument(
        "--logFilePath",
        default=f"{Path.home()}/dotfiles-install.log",
        help="specifies the path where the log file will be saved",
        type=str,
    )
    parser.add_argument("--version", action="version", version=__version__)
    return cast(Arguments, vars(parser.parse_args(arguments)))


def _configureLogging(logFilePath: str) -> None:
    configureLogging(
        level=LOGGING_LEVEL_INFO,
        format="[%(asctime)s] [%(levelname)s]: %(message)s",
        handlers=[FileHandler(getAbsolutePath(logFilePath)), StreamHandler()],
    )
    logWarnings(True)


def main() -> None:
    """Entrypoint of the program."""
    parsedArguments = _parseArguments(argv[1:])
    _configureLogging(parsedArguments["logFilePath"])

    try:
        install()
    except Exception as exception:
        logException("Installation failed.")
        raise exception
