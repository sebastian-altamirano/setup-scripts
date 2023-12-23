"""Contains tests for the installation step defined in `configure_git.py`."""

# pylint: disable=missing-function-docstring

from unittest import TestCase
from unittest.mock import Mock, call, patch

from dotfiles.installation_steps import configureGit
from dotfiles.type_definitions import (
    BasicGitConfiguration,
    GitConfiguration,
    GitConfigurationWithGpgCommitSigning,
)


@patch("dotfiles.installation_steps.configure_git.formatConfigurationBlocks")
@patch("dotfiles.installation_steps.configure_git.getDirectoryName")
@patch("dotfiles.installation_steps.configure_git.joinPaths")
@patch("dotfiles.installation_steps.configure_git.getAbsolutePath")
@patch("dotfiles.installation_steps.configure_git.createOrUpdateFile")
@patch("dotfiles.installation_steps.configure_git.changeResourceMode")
@patch("dotfiles.installation_steps.configure_git.createDirectories")
@patch("dotfiles.installation_steps.configure_git.runWithSh")
@patch("dotfiles.installation_steps.configure_git.copyConfiguration")
class ConfigureGitTests(TestCase):
    """Contains tests for the `configureGit` function."""

    def setUp(self) -> None:
        self.gpgKeyId = "BIH6SLDZCKZ7L8TG2BCTY4HDIT0MOZUQQNTZ8HOF"
        self.gpgKeyInformation = (
            "sec   rsa4096 2024-01-01 [SC]\n"
            f"{self.gpgKeyId}\n"
            "uid                      John Doe <john.doe@example.com>\n"
            "ssb   rsa4096 2024-01-01 [E]\n"
        )
        self.gitConfigurationWithoutCommitSigning: BasicGitConfiguration = {
            "userName": "John Doe",
            "email": "john.doe@example.com",
        }
        self.gitConfigurationWithSshAccess: BasicGitConfiguration = {
            **self.gitConfigurationWithoutCommitSigning,
            "ssh": {
                "cachePassPhraseDuringSession": True,
                "hostname": "github.com",
                "privateKeyName": "id_ed25519",
                "publicKeyName": "id_ed25519.pub",
            },
        }
        self.gitConfigurationWithGpgCommitSigning: GitConfigurationWithGpgCommitSigning = {
            **self.gitConfigurationWithoutCommitSigning,
            "gpg": {
                "privateKeyName": "github.gpg",
            },
            "signingMethod": "gpg",
        }

    def testIfGpgKeyIdIsParsedCorrectly(
        self,
        _mockCopyConfiguration: Mock,
        mockRunWithSh: Mock,
        _mockCreateDirectories: Mock,
        _mockChangeResourceMode: Mock,
        _mockCreateOrUpdateFile: Mock,
        _mockGetAbsolutePath: Mock,
        _mockJoinPaths: Mock,
        _mockGetDirectoryName: Mock,
        _mockFormatConfigurationBlocks: Mock,
    ) -> None:
        mockRunWithSh.return_value.stdout = self.gpgKeyInformation

        configureGit(self.gitConfigurationWithGpgCommitSigning)

        mockRunWithSh.assert_any_call("git", "config", "--global", "user.signingkey", self.gpgKeyId)

    def testIfGpgKeyTrustLevelIsChangedToUltimate(
        self,
        _mockCopyConfiguration: Mock,
        mockRunWithSh: Mock,
        _mockCreateDirectories: Mock,
        _mockChangeResourceMode: Mock,
        _mockCreateOrUpdateFile: Mock,
        _mockGetAbsolutePath: Mock,
        _mockJoinPaths: Mock,
        _mockGetDirectoryName: Mock,
        _mockFormatConfigurationBlocks: Mock,
    ) -> None:
        mockRunWithSh.return_value.stdout = self.gpgKeyInformation

        configureGit(self.gitConfigurationWithGpgCommitSigning)

        mockRunWithSh.assert_any_call(
            "gpg", "--import-ownertrust", pipedInput=f"{self.gpgKeyId}:6:\n"
        )

    def testIfGpgAgentConfigurationIsCreated(
        self,
        _mockCopyConfiguration: Mock,
        mockRunWithSh: Mock,
        _mockCreateDirectories: Mock,
        _mockChangeResourceMode: Mock,
        mockCreateOrUpdateFile: Mock,
        _mockGetAbsolutePath: Mock,
        _mockJoinPaths: Mock,
        _mockGetDirectoryName: Mock,
        mockFormatConfigurationBlocks: Mock,
    ) -> None:
        gitConfiguration: GitConfiguration = {
            **self.gitConfigurationWithoutCommitSigning,
            "commitSigning": {
                "allowCommittingFromVSCode": True,
            },
            "gpg": {
                "cachePassPhraseDuringSession": True,
                "privateKeyName": "github.gpg",
            },
            "signingMethod": "gpg",
        }
        mocksManager = Mock()
        mocksManager.attach_mock(mockCreateOrUpdateFile, "mockCreateOrUpdateFile")
        mocksManager.attach_mock(mockRunWithSh, "mockRunWithSh")

        configureGit(gitConfiguration)

        mockFormatConfigurationBlocks.assert_called_once()
        mocksManager.assert_has_calls(
            [
                call.mockCreateOrUpdateFile(
                    "~/.gnupg/gpg-agent.conf", mockFormatConfigurationBlocks.return_value
                ),
                call.mockRunWithSh("gpg-connect-agent", "reloadagent", "/bye"),
            ]
        )

    def testIfGpgAgentConfigurationIsNotCreated(
        self,
        _mockCopyConfiguration: Mock,
        mockRunWithSh: Mock,
        _mockCreateDirectories: Mock,
        _mockChangeResourceMode: Mock,
        mockCreateOrUpdateFile: Mock,
        _mockGetAbsolutePath: Mock,
        _mockJoinPaths: Mock,
        _mockGetDirectoryName: Mock,
        mockFormatConfigurationBlocks: Mock,
    ) -> None:
        mocksManager = Mock()
        mocksManager.attach_mock(mockCreateOrUpdateFile, "mockRunWithSh")
        mocksManager.attach_mock(mockRunWithSh, "mockRunWithSh")

        configureGit(self.gitConfigurationWithGpgCommitSigning)

        mockFormatConfigurationBlocks.assert_not_called()
        self.assertTrue(
            call("~/.gnupg/gpg-agent.conf", mockFormatConfigurationBlocks.return_value)
            not in mockCreateOrUpdateFile.mock_calls
        )
        self.assertTrue(
            call(
                "gpg-connect-agent",
                "reloadagent",
                "/bye",
                mockFormatConfigurationBlocks.return_value,
            )
            not in mockRunWithSh.mock_calls
        )

    def testIfSshKeyIsCopiedWithTheCorrectPermissions(
        self,
        mockCopyConfiguration: Mock,
        _mockRunWithSh: Mock,
        mockCreateDirectories: Mock,
        mockChangeResourceMode: Mock,
        _mockCreateOrUpdateFile: Mock,
        _mockGetAbsolutePath: Mock,
        _mockJoinPaths: Mock,
        _mockGetDirectoryName: Mock,
        _mockFormatConfigurationBlocks: Mock,
    ) -> None:
        mocksManager = Mock()
        mocksManager.attach_mock(mockCreateDirectories, "mockCreateDirectories")
        mocksManager.attach_mock(mockCopyConfiguration, "mockCopyConfiguration")
        mocksManager.attach_mock(mockChangeResourceMode, "mockChangeResourceMode")
        publicKeyName = self.gitConfigurationWithSshAccess["ssh"]["publicKeyName"]
        privateKeyName = self.gitConfigurationWithSshAccess["ssh"]["privateKeyName"]

        configureGit(self.gitConfigurationWithSshAccess)

        mocksManager.assert_has_calls(
            [
                call.mockCopyConfiguration(".gitconfig", "~/.gitconfig"),
                call.mockCreateDirectories("~/.ssh", mode=0o700),
                call.mockCopyConfiguration(publicKeyName, "~/.ssh"),
                call.mockChangeResourceMode(f"~/.ssh/{publicKeyName}", 0o644),
                call.mockCopyConfiguration(privateKeyName, "~/.ssh"),
                call.mockChangeResourceMode(f"~/.ssh/{privateKeyName}", 0o600),
            ]
        )
