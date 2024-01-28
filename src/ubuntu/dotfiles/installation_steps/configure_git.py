"""Defines an installation step to configure Git."""

from logging import info as logInfo
from os import chmod as changeResourceMode
from os import makedirs as createDirectories
from os.path import join as joinPaths
from subprocess import CalledProcessError
from typing import List, Optional

from dotfiles.helpers.constants import PROJECT_SCRIPTS_PATH, USER_SETTINGS_PATH
from dotfiles.helpers.decorators.installation_step import installationStep
from dotfiles.helpers.utils.copy_configuration import copyConfiguration
from dotfiles.helpers.utils.create_or_update_file import createOrUpdateFile
from dotfiles.helpers.utils.format_configuration_blocks import formatConfigurationBlocks
from dotfiles.helpers.utils.get_absolute_path import getAbsolutePath
from dotfiles.helpers.utils.run_with import runWithSh
from dotfiles.type_definitions import (
    GitCommitSigningConfiguration,
    GitConfiguration,
    GpgConfiguration,
    SshConfiguration,
)


def _configureSshAccess(sshConfiguration: SshConfiguration) -> None:
    sshDirectoryPath = getAbsolutePath(joinPaths("~", ".ssh"))

    # Copy the public and private keys.
    try:
        createDirectories(sshDirectoryPath, mode=0o700)
    except OSError:
        changeResourceMode(sshDirectoryPath, 0o700)

    publicKeyName = sshConfiguration["publicKeyName"]
    publicKeyPath = joinPaths(sshDirectoryPath, publicKeyName)
    copyConfiguration(publicKeyName, sshDirectoryPath)
    changeResourceMode(publicKeyPath, 0o644)

    privateKeyName = sshConfiguration["privateKeyName"]
    privateKeyPath = joinPaths(sshDirectoryPath, privateKeyName)
    copyConfiguration(privateKeyName, sshDirectoryPath)
    changeResourceMode(privateKeyPath, 0o600)

    # Add the SSH agent configuration.
    hostname = sshConfiguration["hostname"]
    createOrUpdateFile(
        joinPaths(sshDirectoryPath, "config"),
        formatConfigurationBlocks(
            [
                [
                    f"Host {hostname}",
                    *(
                        "\tAddKeysToAgent yes"
                        if sshConfiguration.get("cachePassPhraseDuringSession", False)
                        else []
                    ),
                    f"\tHostName {hostname}",
                    "\tIdentitiesOnly yes",
                    f"\tIdentityFile {privateKeyPath}",
                ]
            ]
        ),
    )

    # Add the key to the SSH agent.
    addSshKeyScriptPath = joinPaths(PROJECT_SCRIPTS_PATH, "add-ssh-key.fish")
    runWithSh(addSshKeyScriptPath, privateKeyPath)

    # Set `ssh-agent` to start automatically.
    createOrUpdateFile(joinPaths("~", ".config", "fish", "config.fish"), "eval $(ssh-agent -c)")


def _configureCommitSigningWithSshKey(sshConfiguration: SshConfiguration) -> None:
    # Add the signing configuration.
    publicKeyPath = getAbsolutePath(joinPaths("~", ".ssh", sshConfiguration["publicKeyName"]))
    runWithSh("git", "config", "--global", "gpg.format", "ssh")
    runWithSh("git", "config", "--global", "user.signingkey", publicKeyPath)

    # NOTE: Commiting from VSCode might not work if the SSH key has a passphrase
    # (I have not tested this):
    # https://github.com/microsoft/vscode/issues/179517


def _configureCommitSigningWithGpgKey(
    gpgConfiguration: GpgConfiguration,
    commitSigningConfiguration: Optional[GitCommitSigningConfiguration] = None,
) -> None:
    privateKeyPath = joinPaths(USER_SETTINGS_PATH, gpgConfiguration["privateKeyName"])

    # Import the key.
    runWithSh("gpg", "--import", privateKeyPath, "--batch")

    # Remove previous signing configuration.
    try:
        runWithSh("git", "config", "--global", "--unset", "gpg.format")
    except CalledProcessError as exception:
        # The command returns 5 when you try to unset an option which does not exist.
        if exception.returncode != 5:
            raise exception

    # Add new signing configuration.
    keyInformation = runWithSh("gpg", "--show-keys", privateKeyPath).stdout
    keyId = keyInformation.split("\n")[1].strip()
    runWithSh("git", "config", "--global", "user.signingkey", keyId)
    runWithSh("git", "config", "--global", "commit.gpgsign", "true")

    # Add the key to the fish startup file.
    createOrUpdateFile(joinPaths("~", ".config", "fish", "config.fish"), "set -gx GPG_TTY (tty)")

    # Change the trust level of the key to ultimate.
    runWithSh("gpg", "--import-ownertrust", pipedInput=f"{keyId}:6:\n")

    # Configure `gpg-agent`.
    if commitSigningConfiguration:
        gpgAgentConfiguration: List[List[str]] = []

        if commitSigningConfiguration.get("allowCommittingFromVSCode", False):
            gpgAgentConfiguration.append(
                [
                    "# Allow committing from VSCode.",
                    'pinentry-program "/mnt/c/Program Files (x86)/Gpg4win/bin/pinentry.exe"',
                ]
            )

        if gpgConfiguration.get("cachePassPhraseDuringSession", False):
            gpgAgentConfiguration.append(
                [
                    "# Cache passphrase for 10 hours.",
                    "default-cache-ttl 36000",
                    "max-cache-ttl 36000",
                ]
            )

        if len(gpgAgentConfiguration) != 0:
            createOrUpdateFile(
                joinPaths("~", ".gnupg", "gpg-agent.conf"),
                formatConfigurationBlocks(gpgAgentConfiguration),
            )
            runWithSh("gpg-connect-agent", "reloadagent", "/bye")


@installationStep
def configureGit(configuration: GitConfiguration) -> None:
    """Configures Git."""
    # Copy the base `.gitconfig` if it exists.
    try:
        logInfo("Trying to copy the base `.gitconfig` file...")
        copyConfiguration(".gitconfig", joinPaths("~", ".gitconfig"))
    except FileNotFoundError:
        logInfo(
            "Could not find a base `.gitconfig` file, proceeding with the rest of the "
            "configurations..."
        )

    runWithSh("git", "config", "--global", "user.name", configuration["userName"])
    runWithSh("git", "config", "--global", "user.email", configuration["email"])

    if "ssh" in configuration:
        logInfo("Configuring SSH access...")
        _configureSshAccess(configuration["ssh"])

    if "signingMethod" not in configuration:
        return

    if configuration["signingMethod"] == "ssh":
        logInfo("Configuring commit signing with the SSH key...")
        _configureCommitSigningWithSshKey(configuration["ssh"])
    else:
        logInfo("Configuring commit signing with a GPG key...")
        _configureCommitSigningWithGpgKey(
            configuration["gpg"], configuration.get("commitSigning", None)
        )
