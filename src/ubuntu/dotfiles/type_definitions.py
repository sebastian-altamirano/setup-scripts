"""Contains type definitions."""

from __future__ import annotations

from typing import List, Literal, TypeVar, Union, final

from typing_extensions import NotRequired, TypedDict


@final
class Arguments(TypedDict):
    """Arguments accepted by the installation script."""

    logFilePath: str


@final
class ApplicationSettingsMapping(TypedDict):
    """Defines a source-destination mapping of a resource located in the `/config/ubuntu` folder.

    Matches what is defined in `/config/settings.schema.json` for `/ubuntu/settingsPath`.
    """

    completionCommands: NotRequired[List[List[str]]]
    destination: str
    resourceName: str
    postInstallationInstructions: NotRequired[str]


@final
class GitCommitSigningConfiguration(TypedDict):
    """Configuration accepted by the Dotfiles to configure Git commit signing.

    Matches what is defined in `/config/settings.schema.json` for `/ubuntu/git/commitSigning`.
    """

    allowCommittingFromVSCode: NotRequired[bool]


@final
class GpgConfiguration(TypedDict):
    """Configuration accepted by the Dotfiles to configure Git commit signing.

    Matches what is defined in `/config/settings.schema.json` for `/ubuntu/git/gpg`.
    """

    cachePassPhraseDuringSession: NotRequired[bool]
    privateKeyName: str


@final
class SshConfiguration(TypedDict):
    """Configuration accepted by the Dotfiles to configure Git access and commit signing.

    Matches what is defined in `/config/settings.schema.json` for `/ubuntu/git/ssh`.
    """

    cachePassPhraseDuringSession: NotRequired[bool]
    hostname: str
    privateKeyName: str
    publicKeyName: str


class _BaseGitConfiguration(TypedDict):
    email: str
    userName: str


@final
class BasicGitConfiguration(_BaseGitConfiguration):
    """Basic configuration accepted by the Dotfiles to configure Git."""

    ssh: NotRequired[SshConfiguration]
    """Used to configure SSH access to the Git provider."""


class _BaseGitConfigurationWithCommitSigning(_BaseGitConfiguration):
    commitSigning: NotRequired[GitCommitSigningConfiguration]


@final
class GitConfigurationWithGpgCommitSigning(_BaseGitConfigurationWithCommitSigning):
    """Configuration accepted by the Dotfiles to configure Git with GPG signing."""

    gpg: GpgConfiguration
    signingMethod: Literal["gpg"]
    ssh: NotRequired[SshConfiguration]


@final
class GitConfigurationWithSshCommitSigning(_BaseGitConfigurationWithCommitSigning):
    """Configuration accepted by the Dotfiles to configure Git with SSH access and signing."""

    signingMethod: Literal["ssh"]
    ssh: SshConfiguration


GitConfiguration = Union[
    BasicGitConfiguration,
    GitConfigurationWithGpgCommitSigning,
    GitConfigurationWithSshCommitSigning,
]
"""Configuration accepted by the Dotfiles to configure Git.

Matches what is defined in `/config/settings.schema.json` for `/ubuntu/git`.
"""


@final
class Config(TypedDict):
    """Configuration accepted by the Dotfiles.

    Matches what is defined in `/config/settings.schema.json` for `/ubuntu`.
    """

    git: NotRequired[GitConfiguration]
    postInstallationInstructions: NotRequired[List[str]]
    settingsPaths: NotRequired[List[ApplicationSettingsMapping]]
    vscodeExtensions: NotRequired[List[str]]


InstallationStepReturnValueT = TypeVar("InstallationStepReturnValueT")
