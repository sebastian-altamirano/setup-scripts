"""Contains type definitions."""

from typing import List, Literal, TypedDict, TypeVar


class Arguments(TypedDict):
    """Arguments accepted by the installation script."""

    logFilePath: str


class _ApplicationSettingsMapping(TypedDict, total=False):
    completionCommands: List[List[str]]
    postInstallationInstructions: str


class ApplicationSettingsMapping(_ApplicationSettingsMapping):
    """Defines a source-destination mapping of a resource located in the `/config/ubuntu` folder.

    Matches what is defined in `/config/settings.schema.json` for the `/ubuntu/settingsPath` JSON
    Pointer.
    """

    resourceName: str
    destination: str


class _GitCommitSigningConfiguration(TypedDict, total=False):
    allowCommittingFromVSCode: bool
    cachePassPhraseDuringSession: bool


class GitCommitSigningConfiguration(_GitCommitSigningConfiguration):
    """Configuration accepted by the Dotfiles to configure Git.

    Matches what is defined in `/config/settings.schema.json` for the
    `/ubuntu/gitConfiguration/commitSigning` JSON Pointer.
    """

    privateKeyName: str
    signingMethod: Literal["gpg", "ssh"]


class _GitConfiguration(TypedDict, total=False):
    commitSigning: GitCommitSigningConfiguration


class GitConfiguration(_GitConfiguration):
    """Configuration accepted by the Dotfiles to configure Git.

    Matches what is defined in `/config/settings.schema.json` for the `/ubuntu/gitConfiguration`
    JSON Pointer.
    """

    email: str
    userName: str


class Config(TypedDict, total=False):
    """Configuration accepted by the Dotfiles.

    Matches what is defined in `/config/settings.schema.json` for the `/ubuntu` JSON Pointer.
    """

    gitConfiguration: GitConfiguration
    postInstallationInstructions: List[str]
    settingsPaths: List[ApplicationSettingsMapping]
    vscodeExtensions: List[str]


InstallationStepReturnValueT = TypeVar("InstallationStepReturnValueT")
