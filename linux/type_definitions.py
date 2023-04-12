"""Contains type definitions."""

from typing import List, TypedDict, TypeVar


class _ApplicationSettingsMapping(TypedDict, total=False):
    completionCommands: List[List[str]]
    postInstallationInstructions: str


class ApplicationSettingsMapping(_ApplicationSettingsMapping):
    """Defines a source-destination mapping of a resource located in the `app-settings` folder.

    Matches what is defined in `/settings.schema.json` for the `settingsPath` key.
    """

    resourceName: str
    destination: str


class Arguments(TypedDict):
    """Arguments accepted by the installation script."""

    logFilePath: str


class Config(TypedDict, total=False):
    """Configuration accepted by the Dotfiles.

    Matches what is defined in `/settings.schema.json`.
    """

    quickAccessFolders: List[str]
    settingsPaths: List[ApplicationSettingsMapping]
    vscodeExtensions: List[str]


InstallationStepReturnValueT = TypeVar("InstallationStepReturnValueT")
