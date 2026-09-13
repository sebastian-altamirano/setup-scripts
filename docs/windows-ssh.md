# Connect to a Windows device over SSH

This guide configures a Windows computer as an SSH server and connects to it from another Windows computer using the terminal and, optionally, VS Code Remote - SSH.

The remote computer can be a physical computer, virtual machine, VPS, or another Windows device.

Most of the setup can be performed from an elevated PowerShell session, so the remote computer does not need to have a graphical interface available.

You need administrator access to the remote computer to install and configure the SSH server, and you must replace values enclosed in angle brackets, such as `<remote hostname>` or `<remote username>`.

## 1. Prepare the remote computer

### Install OpenSSH Server

First, try installing OpenSSH Server as a Windows optional feature from an elevated PowerShell window:

```pwsh
$capability = Get-WindowsCapability -Online | Where-Object Name -like 'OpenSSH.Server*' | Select-Object -First 1
if ($capability.State -eq 'NotPresent') {
    Add-WindowsCapability -Online -Name $capability.Name
}
```

If no capability is returned, or if `Add-WindowsCapability` is unavailable, fails, or remains stuck, install the server from the latest [Win32-OpenSSH release](https://github.com/PowerShell/Win32-OpenSSH/releases).

That fallback involves downloading the Windows Installer (`.msi`) for the appropriate architecture, copying it to the remote computer, and running it with administrator privileges:

```pwsh
msiexec /i "$env:UserProfile\<OpenSSH installer>.msi" ADDLOCAL=Server
```

Depending on how the remote computer can be accessed, downloading or launching the installer may require a GUI or a separate way to transfer and execute the file; this guide does not cover a fully automated GitHub-download-and-install workflow.

Verify that the service exists:

```pwsh
Get-Service -Name sshd
```

If necessary, start it from an elevated PowerShell window:

```pwsh
Start-Service sshd
```

If the service was installed but is not configured to start automatically, enable that behavior with:

```pwsh
Set-Service -Name sshd -StartupType Automatic
```

## 2. Create an SSH key on the local computer

Run this command on the computer from which you will connect:

```pwsh
ssh-keygen -t ed25519 -C "<comment or email>"
```

Use the default path unless you need a separate key, and optionally protect the private key with a passphrase.

The public key will be stored at `~\.ssh\id_ed25519.pub` and the private key at `~\.ssh\id_ed25519`.

Never copy or share the private key.

## 3. Add the public key to the remote computer

Display the public key on the local computer and copy the complete line:

```pwsh
Get-Content ~/.ssh/id_ed25519.pub
```

On the remote computer, open an elevated PowerShell window and run:

```pwsh
$sshDir = Join-Path $env:USERPROFILE 'ssh'
New-Item -ItemType Directory -Path $sshDir -Force | Out-Null

$authKeys = Join-Path $sshDir 'authorized_keys'
Set-Content -Path $authKeys -Value "<paste the public key here>"

icacls $sshDir /inheritance:r
icacls $sshDir /remove:g "Users" "Administrators" "Everyone"
icacls $sshDir /grant:r "$($env:USERNAME):(F)"

icacls $authKeys /inheritance:r
icacls $authKeys /remove:g "Users" "Administrators" "Everyone"
icacls $authKeys /grant:r "$($env:USERNAME):(R,W)"
```

If `icacls` cannot find `Users`, `Administrators`, or `Everyone`, replace those names with the corresponding localized group names on the remote computer.

> Normally, the file is created at `.ssh\authorized_keys`. This guide uses `ssh\authorized_keys` because some restricted environments periodically delete the file from its default location.

## 4. Configure the SSH server

From an elevated PowerShell window, replace the existing configuration with:

```pwsh
$configPath = 'C:\ProgramData\ssh\sshd_config'
$sshdConfig = @'
# Use public-key authentication only.
PasswordAuthentication no
ChallengeResponseAuthentication no
PubkeyAuthentication yes
AuthorizedKeysFile C:/Users/<remote username>/ssh/authorized_keys

# Required by VS Code Remote - SSH.
Subsystem sftp sftp-server.exe

# Conservative session limits.
MaxAuthTries 3
MaxSessions 5

# Use a custom port to reduce automated scans of the default SSH port.
Port 46283
'@

Set-Content -Path $configPath -Value $sshdConfig -Encoding ascii
```

> Note: Windows Firewall or other network controls between the two computers may block connections to this port.

Restart the service:

```pwsh
Restart-Service sshd
```

## 5. Find the connection details

On the remote computer, run:

```pwsh
whoami
hostname
```

For `whoami`, use only the username after the backslash.

Use the hostname returned by `hostname`, the username from `whoami`, and the configured SSH port in the connection settings below.

## 6. Connect from the terminal

Create or edit `~\.ssh\config` on the local computer and add:

```text
Host windows-remote
    HostName <remote hostname>
    User <remote username>
    HostKeyAlias windows-remote
    IdentityFile ~/.ssh/id_ed25519
    IdentitiesOnly yes
    PreferredAuthentications publickey
    PubkeyAuthentication yes
    StrictHostKeyChecking accept-new
    UserKnownHostsFile ~/.ssh/known_hosts
    Port 46283
```

Test the connection:

```pwsh
ssh windows-remote
```

The first time, verify and accept the server fingerprint when prompted, then enter the key passphrase if you configured one.

## 7. Optional: connect with VS Code

Install [VS Code](https://code.visualstudio.com/) and the Microsoft [Remote - SSH extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-ssh) on the local computer.

Add these entries to VS Code's user settings if they are not already present:

```jsonc
"remote.autoForwardPortsSource": "hybrid",
"remote.SSH.configFile": "~\\.ssh\\config",
"remote.SSH.path": "C:\\Windows\\System32\\OpenSSH\\ssh.exe",
"remote.SSH.remotePlatform": {
    "*": "windows"
}
```

Run `Remote-SSH: Connect to Host` and select `windows-remote`.

VS Code installs VS Code Server on the remote computer during connection; if that installation or a later update fails, test the terminal connection first with `ssh windows-remote`.

### Port forwarding

VS Code may fail to forward an application's port or may forward it to a different local port than expected, for example forwarding remote port 5000 to local port 5001.

Use the Ports panel to see which remote ports are open, add or remove forwarded ports, edit their forwarding settings, and check which local port each remote port is using.

## Optional: persist Git credentials on the remote computer

This is only useful if you use Git over HTTPS from an SSH session on the remote computer.

By default, Git uses `wincredman` to persist credentials, but it does not work in SSH sessions, so you must enter your credentials manually each time you perform an operation against a remote repository.

Configure Git Credential Manager to use Windows DPAPI instead:

```pwsh
git config --global credential.credentialStore dpapi
```

If the DPAPI cache becomes invalid, remove it and authenticate again:

```pwsh
Remove-Item ~\.gcm\dpapi_store -Recurse
```

## Troubleshooting

If the terminal connection fails, check that the `sshd` service is running, the configured port is reachable, the public-key path matches `AuthorizedKeysFile`, and the ACLs allow the remote user to read the key file.

For detailed SSH diagnostics, run:

```pwsh
ssh -vvvv windows-remote
```

For VS Code-specific failures, inspect the `Remote SSH` channel in the Output panel after confirming that the terminal connection works.

### The remote hostname changed

A VM or VPS may change its hostname after being stopped or restarted.

This can happen automatically after a long period without use, depending on how the environment is managed.

Run `hostname` on the remote computer and update `HostName` in `~\.ssh\config` when necessary.
