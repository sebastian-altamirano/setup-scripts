# Windows Setup - Part 2 (Final).
# Runs automatically after Part 1.
# Requires restart.

#Requires -RunAsAdministrator


# Import utility functions.
. "$PSScriptRoot\utils.ps1"

$CONFIG_PATH = Join-Path $PSScriptRoot '..\config' | Resolve-Path


$ErrorActionPreference = 'Stop'
trap {
	if ($shutdownBlocker) {
		Stop-Job $shutdownBlocker -ErrorAction SilentlyContinue
		Remove-Job $shutdownBlocker -ErrorAction SilentlyContinue
	}

	Write-ErrorMsg 'An error occurred. Check the log for details.'
	Stop-Transcript
	exit 1
}

Start-Transcript -Path "$PSScriptRoot\setup-part-2.log" -Append

Write-InfoMsg '===== Windows Dotfiles Setup - Part 2 (Final) ====='
Write-AttentionMsg "The script will install many applications and may require your attention. Please do not leave your computer unattended.`n"

# Remove the scheduled task that ran this script.
Unregister-ScheduledTask -TaskName 'DotfilesSetupPart2' -Confirm:$false

# Workaround for https://github.com/microsoft/winget-cli/issues/229:
# Starts a background job to abort shutdowns triggered by some installers.
# This helps prevent unexpected restarts, but won't catch all cases.
$shutdownBlocker = Start-Job {
	while ($true) {
		shutdown -a 2>$null
		Start-Sleep -Seconds 2
	}
}

Write-InfoMsg 'Installing WinGet packages...'
$winGetPackages = @(
	'ArminOsaj.AutoDarkMode',
	'DevToys-app.DevToys',
	'Discord.Discord',
	'DuongDieuPhap.ImageGlass',
	'FlawlessWidescreen.FlawlessWidescreen',
	'Guru3D.Afterburner',
	'JanDeDobbeleer.OhMyPosh',
	'KDE.Krita',
	'Logitech.GHUB',
	'M2Team.NanaZip',
	'Meta.Oculus',
	'Microsoft.PowerToys',
	'Microsoft.VisualStudioCode',
	'Microsoft.WindowsTerminal',
	'mtkennerly.ludusavi',
	'Philips.HueSync',
	'REALiX.HWiNFO',
	'Reshade.Setup.AddonsSupport',
	'Spotify.Spotify',
	'Valve.Steam',
	# Microsoft Store apps:
	'9N0866FS04W8', # Dolby Access
	'XPDDT99J9GKB5C', # Samsung Magician
	'9MV0B5HZVK9Z', # Xbox
	'9NBLGGH30XJ3'    # Xbox Accessories
)
foreach ($package in $winGetPackages) {
	winget install --exact --id $package --accept-package-agreements --accept-source-agreements --silent
}

Write-InfoMsg 'Installing Scoop (for packages not available in WinGet)...'
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
Invoke-RestMethod -Uri https://get.scoop.sh | Invoke-Expression

Write-InfoMsg 'Installing Scoop packages...'
scoop bucket add nerd-fonts
scoop install nerd-fonts/Monaspace-NF

Write-InfoMsg 'Installing PowerShell modules...'
Set-PSRepository -Name 'PSGallery' -InstallationPolicy Trusted
Install-Module -Name z

Write-InfoMsg 'Installing VS Code extensions...'
$extensions = @(
	'GitHub.github-vscode-theme',
	'jgclark.vscode-todo-highlight',
	'ms-vscode-remote.remote-wsl'
)
foreach ($extension in $extensions) {
	code --install-extension $extension
}

Write-InfoMsg 'Copying configuration files...'

# PowerShell profile.
New-Item -ItemType Directory -Path (Split-Path $PROFILE) -Force | Out-Null
Copy-Item "$CONFIG_PATH\powershell-profile.ps1" $PROFILE

# VS Code settings.
$vscodeSettingsPath = "$env:AppData\Code\User"
New-Item -ItemType Directory -Path $vscodeSettingsPath -Force | Out-Null
Copy-Item "$CONFIG_PATH\vscode-settings.jsonc" "$vscodeSettingsPath\settings.json"
Copy-Item "$CONFIG_PATH\vscode-keybindings.jsonc" "$vscodeSettingsPath\keybindings.json"

# Windows Terminal settings.
$wtSettingsPath = "$env:LocalAppData\Packages\Microsoft.WindowsTerminal_8wekyb3d8bbwe\LocalState"
New-Item -ItemType Directory -Path $wtSettingsPath -Force | Out-Null
Copy-Item "$CONFIG_PATH\windows-terminal.jsonc" "$wtSettingsPath\settings.json"

Write-InfoMsg 'Installing Ubuntu in WSL...'
wsl --install -d Ubuntu

Stop-Job $shutdownBlocker
Remove-Job $shutdownBlocker

Write-SuccessMsg "`nPart 2 (Final) complete."
Write-SuccessMsg 'Once restarted, check the README.md for the next steps.'
Write-AttentionMsg 'Press Enter to restart the computer.'
$null = Read-Host
Stop-Transcript
Restart-Computer
