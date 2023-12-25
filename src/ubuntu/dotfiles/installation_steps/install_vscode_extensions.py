"""Defines an installation step for installing VSCode extensions."""

from logging import error as logError
from logging import info as logInfo
from typing import List

from dotfiles.helpers.utils import installationStep, runWithSh


@installationStep
def installVSCodeExtensions(extensions: List[str]) -> None:
    """Installs extensions for VSCode."""
    extensionThatCouldNotBeInstalled = ""
    for extension in extensions:
        commandOutput = runWithSh("code", "--install-extension", extension)
        if commandOutput.stderr:
            extensionThatCouldNotBeInstalled += f"- {extension}\n"

    if extensionThatCouldNotBeInstalled:
        logError(
            "Could not install the following extensions:\n%s",
            extensionThatCouldNotBeInstalled,
        )
    else:
        logInfo("All extensions have been installed successfully.")
