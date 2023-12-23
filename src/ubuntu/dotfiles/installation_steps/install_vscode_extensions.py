"""Defines an installation step for installing VSCode extensions."""

from logging import error as logError
from logging import info as logInfo
from subprocess import run
from typing import List

from dotfiles.helpers.utils import installationStep

runWithoutLogging = run


@installationStep
def installVSCodeExtensions(extensions: List[str]) -> None:
    """Installs extensions for VSCode."""
    extensionThatCouldNotBeInstalled = ""
    for extension in extensions:
        commandOutput = runWithoutLogging(
            ["code", "--install-extension", extension], capture_output=True, check=True
        )
        if commandOutput.stderr:
            extensionThatCouldNotBeInstalled += f"- {extension}\n"

    if extensionThatCouldNotBeInstalled:
        logError(
            "Could not install the following extensions:\n%s",
            extensionThatCouldNotBeInstalled,
        )
    else:
        logInfo("All extensions have been installed successfully.")
