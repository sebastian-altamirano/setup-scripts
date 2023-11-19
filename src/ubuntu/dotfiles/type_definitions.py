"""Contains type definitions."""

from typing import List, TypedDict, TypeVar


class Arguments(TypedDict):
    """Arguments accepted by the installation script."""

    logFilePath: str


class _ApplicationSettingsMapping(TypedDict, total=False):
    completionCommands: List[List[str]]
    postInstallationInstructions: str


class ApplicationSettingsMapping(_ApplicationSettingsMapping):
    """Defines a source-destination mapping of a resource located in the `/config/ubuntu` folder.

    Matches what is defined in `/config/settings.schema.json` for the `settingsPath` key.
    """

    resourceName: str
    destination: str


class GitConfiguration(TypedDict):
    """Configuration accepted by the Dotfiles to configure Git.

    Matches what is defined in `/config/settings.schema.json` for the `gitConfiguration` key.
    """

    email: str
    userName: str


class Config(TypedDict, total=False):
    """Configuration accepted by the Dotfiles.

    Matches what is defined in `/config/settings.schema.json`.
    """

    gitConfiguration: GitConfiguration
    postInstallationInstructions: List[str]
    settingsPaths: List[ApplicationSettingsMapping]
    vscodeExtensions: List[str]


InstallationStepReturnValueT = TypeVar("InstallationStepReturnValueT")
