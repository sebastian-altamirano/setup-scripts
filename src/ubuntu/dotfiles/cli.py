"""Defines the aplication entry point."""

from argparse import ArgumentParser
from datetime import datetime
from logging import INFO as LOGGING_LEVEL_INFO
from logging import FileHandler, StreamHandler
from logging import basicConfig as configureLogging
from logging import captureWarnings as logWarnings
from logging import exception as logException
from os.path import join as joinPaths
from pathlib import Path
from sys import argv
from typing import Optional, Sequence, cast

from dotfiles import __version__
from dotfiles.helpers.utils.get_absolute_path import getAbsolutePath
from dotfiles.install import install
from dotfiles.read_and_validate_config import readAndValidateConfig
from dotfiles.type_definitions import Arguments


def _parseArguments(arguments: Optional[Sequence[str]] = None) -> Arguments:
    parser = ArgumentParser(description="Installation script for Ubuntu dotfiles.")
    parser.add_argument(
        "--logFilePath",
        default=(
            joinPaths(
                Path.home(), f"dotfiles_install-{datetime.now().strftime('%Y_%m_%d-%H_%M_%S')}.log"
            )
        ),
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
        install(readAndValidateConfig())
    except Exception as exception:
        logException("Installation failed.")
        raise exception
