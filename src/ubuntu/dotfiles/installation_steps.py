"""Contains functions to perform each of the steps that make up the installation script."""

from logging import error as logError
from logging import info as logInfo
from os import chmod as changeResourceMode
from os import makedirs as createDirectories
from os.path import abspath as getAbsolutePath
from os.path import dirname as getDirectoryName
from os.path import join as joinPaths
from subprocess import CalledProcessError, run
from typing import List

from dotfiles.helpers.utils import (
    copyConfiguration,
    createOrUpdateFile,
    formatConfigurationBlocks,
    installationStep,
    runWithFish,
    runWithSh,
)
from dotfiles.type_definitions import ApplicationSettingsMapping, GitConfiguration

runWithoutLogging = run


@installationStep
def configureGit(configuration: GitConfiguration) -> None:  # pylint: disable=too-many-statements
    """Configures Git."""
    # Copy the base `.gitconfig` if it exists.
    try:
        logInfo("Trying to copy the base `.gitconfig` file...")
        copyConfiguration(".gitconfig", "~/.gitconfig")
    except FileNotFoundError:
        logInfo(
            "Could not find a base `.gitconfig` file, proceeding with the rest of the "
            "configurations..."
        )

    runWithSh("git", "config", "--global", "user.name", configuration["userName"])
    runWithSh("git", "config", "--global", "user.email", configuration["email"])

    # Configure SSH access.
    if "ssh" in configuration:
        logInfo("Configuring SSH access...")
        sshConfiguration = configuration["ssh"]

        # Copy the public and private keys.
        try:
            createDirectories("~/.ssh", mode=0o700)
        except OSError:
            changeResourceMode("~/.ssh", 0o700)

        publicKeyName = sshConfiguration["publicKeyName"]
        publicKeyPath = f"~/.ssh/{publicKeyName}"
        copyConfiguration(publicKeyName, "~/.ssh")
        changeResourceMode(publicKeyPath, 0o644)

        privateKeyName = sshConfiguration["privateKeyName"]
        privateKeyPath = f"~/.ssh/{privateKeyName}"
        copyConfiguration(privateKeyName, "~/.ssh")
        changeResourceMode(privateKeyPath, 0o600)

        # Add the SSH agent configuration.
        hostname = sshConfiguration["hostname"]
        createOrUpdateFile(
            "~/.ssh/config",
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
        addSshKeyScriptPath = joinPaths(
            getDirectoryName(getAbsolutePath(__file__)), "scripts/add-ssh-key.fish"
        )
        runWithSh(addSshKeyScriptPath, privateKeyPath)

        # Set `ssh-agent` to start automatically.
        createOrUpdateFile("~/.config/fish/config.fish", "eval $(ssh-agent -c)")

    if "signingMethod" not in configuration:
        return

    if configuration["signingMethod"] == "ssh":
        logInfo("Configuring commit signing with the SSH key...")

        # Add the signing configuration.
        publicKeyPath = f"~/.ssh/{configuration['ssh']['publicKeyName']}"
        runWithSh("git", "config", "--global", "gpg.format", "ssh")
        runWithSh("git", "config", "--global", "user.signingkey", publicKeyPath)

        # NOTE: Commiting from VSCode might not work if the SSH key has a passphrase
        # (I have not tested this):
        # https://github.com/microsoft/vscode/issues/179517
    else:
        logInfo("Configuring commit signing with a GPG key...")
        gpgConfiguration = configuration.get("gpg", None)

        privateKeyPath = getAbsolutePath(
            f"../../../config/ubuntu/{gpgConfiguration['privateKeyName']}"
        )

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
        createOrUpdateFile("~/.config/fish/config.fish", "set -gx GPG_TTY (tty)")

        # Change the trust level of the key to ultimate.
        runWithSh("gpg", "--import-ownertrust", pipedInput=f"{keyId}:6:\n")

        # Configure `gpg-agent`.
        if "commitSigning" in configuration:
            gpgAgentConfiguration: List[List[str]] = []
            commitSigningConfiguration = configuration["commitSigning"]

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
                    "~/.gnupg/gpg-agent.conf", formatConfigurationBlocks(gpgAgentConfiguration)
                )
                runWithSh("gpg-connect-agent", "reloadagent", "/bye")


@installationStep
def installFish() -> None:
    """Installs fish and changes the default shell to it."""
    runWithSh("sudo", "apt-add-repository", "-y", "ppa:fish-shell/release-3")
    runWithSh("sudo", "apt", "-y", "install", "fish")

    logInfo("Changing the default shell to fish...")
    runWithSh(
        "sudo",
        "chsh",
        "-s",
        run(["which", "fish"], capture_output=True, check=True, text=True).stdout.rstrip(),
        run(["whoami"], capture_output=True, check=True, text=True).stdout.rstrip(),
    )


@installationStep
def upgradeSystemDependencies() -> None:
    """Upgrades system packages using apt."""
    runWithSh("sudo", "apt", "update")
    runWithSh("sudo", "apt", "-y", "upgrade")


@installationStep
def installPackages() -> List[str]:
    """Installs packages and plugins and returns post-installation instructions."""
    postInstallationInstructions: List[str] = []

    logInfo("Installing fisher...")
    # Fisher is installed using an script because it requires `source`, which cannot be executed
    # with `subprocess.run`.
    fisherInstallationScriptPath = joinPaths(
        getDirectoryName(getAbsolutePath(__file__)), "scripts/install-fisher.fish"
    )
    runWithSh(fisherInstallationScriptPath)

    logInfo("Installing some plugins for fisher...")
    runWithFish("fisher", "install", "IlanCosman/tide@v5")
    postInstallationInstructions.append("Run `tide configure` to configure the aspect of fish.")
    runWithFish("fisher", "install", "jethrokuan/z")
    runWithFish("fisher", "install", "jorgebucaran/nvm.fish")

    logInfo("Installing Node LTS...")
    runWithFish("nvm", "install", "lts")
    runWithFish("set", "--universal", "nvm_default_version", "lts")
    runWithSh("npm", "i", "-g", "npm")

    logInfo("Installing Git...")
    runWithSh("sudo", "apt", "-y", "install", "git")

    return postInstallationInstructions


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


@installationStep
def copyApplicationSettings(settingsMappings: List[ApplicationSettingsMapping]) -> List[str]:
    """Copies applications settings and return post-installation instructions."""
    postInstallationInstructions: List[str] = []

    for settingsMapping in settingsMappings:
        logInfo(
            'Copying "%s" to "%s"...',
            settingsMapping["resourceName"],
            settingsMapping["destination"],
        )

        try:
            copyConfiguration(settingsMapping["resourceName"], settingsMapping["destination"])
        except FileNotFoundError:
            logError(
                'Could not copy "%s" because the resource does not exist.',
                settingsMapping["resourceName"],
            )

        if "completionCommands" in settingsMapping:
            logInfo("Running completion commands...")
            for commandArgs in settingsMapping["completionCommands"]:
                runWithSh(*commandArgs)

        if "postInstallationInstructions" in settingsMapping:
            postInstallationInstructions.append(settingsMapping["postInstallationInstructions"])

    return postInstallationInstructions
