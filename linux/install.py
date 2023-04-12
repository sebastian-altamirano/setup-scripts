#!/usr/bin/python3

"""Installation script for Linux dotfiles."""

from argparse import ArgumentParser
from json import loads as readJson
from logging import INFO as LOGGING_LEVEL_INFO
from logging import FileHandler, StreamHandler
from logging import basicConfig as configureLogging
from logging import captureWarnings as logWarnings
from logging import exception as logException
from os.path import abspath as getAbsolutePath
from pathlib import Path
from sys import argv
from typing import List, Optional, Sequence, cast

from linux.helpers.utils import logCompletionMessage, warnAboutUnsupportedConfig
from linux.installation_steps import (
    copyApplicationSettings,
    installFish,
    installPackages,
    installVSCodeExtensions,
    upgradeSystemDependencies,
)
from linux.type_definitions import Arguments, Config

UNSUPPORTED_CONFIGURATION_KEYS = [
    # This is not supported because this program is intended to be run inside WSL.
    "quickAccessFolders"
]


def install() -> None:
    """Installs Linux dotfiles.

    Upgrades dependencies, installs packages and copies applications settings.
    """
    postInstallationInstructions: List[str] = []

    installFish()
    upgradeSystemDependencies()
    postInstallationInstructions += installPackages()

    config: Config = readJson("settings.json")
    for key in UNSUPPORTED_CONFIGURATION_KEYS:
        if key in config:
            warnAboutUnsupportedConfig(key)
    if "vscodeExtensions" in config:
        installVSCodeExtensions(config["vscodeExtensions"])
    if "settingsPaths" in config:
        postInstallationInstructions += copyApplicationSettings(config["settingsPaths"])

    logCompletionMessage(postInstallationInstructions)


def _parseArguments(arguments: Optional[Sequence[str]] = None) -> Arguments:
    parser = ArgumentParser(description="Installation script for Linux dotfiles.")
    parser.add_argument(
        "--logFilePath",
        default=f"{Path.home()}/dotfiles-install.log",
        help="specifies the path where the log file will be saved",
        type=str,
    )
    parser.add_argument("--version", action="version", version="1.0.0")
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


if __name__ == "__main__":
    main()
