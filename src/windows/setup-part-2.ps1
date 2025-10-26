# Windows Setup - Part 2 (Final).
# Runs automatically after Part 1.
# Requires restart.

#Requires -RunAsAdministrator

# Import utility functions.
. "$PSScriptRoot\utils.ps1"

$CONFIG_PATH = Join-Path $PSScriptRoot '..\config' | Resolve-Path

$ErrorActionPreference = 'Stop'

$LOG_PATH = Join-Path $PSScriptRoot 'windows-setup-part-2.log'
Start-Transcript -Path $LOG_PATH -Append

try {
	Write-InfoMsg '===== Windows Setup - Part 2 (Final) ====='
	Write-AttentionMsg (
		"The script will install many applications and may require your attention. " +
		"Please do not leave your computer unattended.`n"
	)

	# Workaround for https://github.com/microsoft/winget-cli/issues/229:
	# Starts a background job to abort shutdowns triggered by some installers.
	# This helps prevent unexpected restarts, but won't catch all cases.
	$shutdownBlocker = Start-Job {
		while ($true) {
			shutdown -a 2>$null
			Start-Sleep -Seconds 2
		}
	}

	Write-InfoMsg 'Uninstalling bundled applications...'
	$uwpPackages = @(
		'BingNews',
		'FeedbackHub',
		'MicrosoftSolitaireCollection',
		'MicrosoftStickyNotes',
		'Outlook'
	)
	foreach ($package in $uwpPackages) {
		Get-AppxPackage -All "*$package*" | Remove-AppxPackage -AllUsers
	}
	$winGetPackages = @(
		'Microsoft.Teams'
		'9WZDNCRD29V9', # Microsoft 365 Copilot
		'9NZBF4GT040C', # Microsoft Bing
		'9NBLGGH5R558', # Microsoft To Do
		'9NMPJ99VJBWV', # Phone Link
		'9NFTCH6J7FHV', # Power Automate
		'9P7BP5VNWKX5', # Quick Assist
		'9PC1H9VN18CM'  # Start Experiences App
	)
	foreach ($package in $winGetPackages) {
		winget uninstall --exact --id $package  --accept-source-agreements --silent
	}
	taskkill /f /im OneDrive.exe
	# OneDrive uninstall returns error code 2147747483, but completes successfully and does not cause
	# the script to enter the catch block.
	winget uninstall 'OneDriveSetup.exe' --accept-source-agreements --silent

	Write-InfoMsg 'Installing WinGet packages...'
	Write-InfoMsg 'Note that some applications might open during installation.'
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
		'mtkennerly.ludusavi',
		'Philips.HueSync',
		'REALiX.HWiNFO',
		'Reshade.Setup.AddonsSupport',
		'Valve.Steam',
		# Microsoft Store apps:
		'9N0866FS04W8',   # Dolby Access
		'XPDDT99J9GKB5C', # Samsung Magician
		'9NCBCSZSJRSB',   # Spotify ('Spotify.Spotify' installer cannot be run from an administrator context)
		'9MV0B5HZVK9Z',   # Xbox
		'9NBLGGH30XJ3'    # Xbox Accessories
	)
	foreach ($package in $winGetPackages) {
		winget install --exact --id $package `
			--accept-package-agreements --accept-source-agreements `
			--silent
	}

	Write-InfoMsg 'Installing fonts...'
	# Refresh PATH to ensure `oh-my-posh` is available.
	$env:Path = [System.Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + `
		[System.Environment]::GetEnvironmentVariable("Path", "User")
	oh-my-posh font install monaspace

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

	Write-InfoMsg 'Copying Oh My Posh theme...'
	Copy-Item "$CONFIG_PATH\ys-custom.omp.json" "$env:UserProfile\ys-custom.omp.json"

	Write-InfoMsg 'Copying Oh My Posh theme toggle script...'
	$pwshScriptsPath = "$([Environment]::GetFolderPath('MyDocuments'))\PowerShell\Scripts"
	New-Item -ItemType Directory -Path $pwshScriptsPath -Force | Out-Null
	Copy-Item "$CONFIG_PATH\update-omp-theme.ps1" "$pwshScriptsPath\update-omp-theme.ps1"
	Unblock-File "$pwshScriptsPath\update-omp-theme.ps1"

	Write-InfoMsg 'Copying Auto Dark Mode settings...'
	$autoDarkModeSettingsPath = "$env:AppData\AutoDarkMode"
	New-Item -ItemType Directory -Path $autoDarkModeSettingsPath -Force | Out-Null
	Copy-Item "$CONFIG_PATH\autodarkmode-config.yaml" "$autoDarkModeSettingsPath\config.yaml"
	Copy-Item "$CONFIG_PATH\autodarkmode-scripts.yaml" "$autoDarkModeSettingsPath\scripts.yaml"

	Write-InfoMsg 'Copying PowerShell profile...'
	New-Item -ItemType Directory -Path (Split-Path $PROFILE) -Force | Out-Null
	# Unblock the downloaded script so it can be executed.
	Unblock-File "$CONFIG_PATH\powershell-profile.ps1"
	Copy-Item "$CONFIG_PATH\powershell-profile.ps1" $PROFILE

	Write-InfoMsg 'Copying VS Code settings...'
	$vscodeSettingsPath = "$env:AppData\Code\User"
	New-Item -ItemType Directory -Path $vscodeSettingsPath -Force | Out-Null
	Copy-Item "$CONFIG_PATH\vscode-settings.jsonc" "$vscodeSettingsPath\settings.json"
	Copy-Item "$CONFIG_PATH\vscode-keybindings.jsonc" "$vscodeSettingsPath\keybindings.json"

	Write-InfoMsg 'Copying Windows Terminal settings...'
	$wtSettingsPath = "$env:LocalAppData\Packages\Microsoft.WindowsTerminal_8wekyb3d8bbwe\LocalState"
	New-Item -ItemType Directory -Path $wtSettingsPath -Force | Out-Null
	Copy-Item "$CONFIG_PATH\windows-terminal.jsonc" "$wtSettingsPath\settings.json"

	Write-InfoMsg 'Installing Ubuntu in WSL...'
	wsl --install -d Ubuntu --no-launch
	Write-InfoMsg 'The Ubuntu installer will prompt you to create a user and set a password.'
	ubuntu.exe install

	Write-InfoMsg 'Running WSL setup script...'
	$wslSetupScriptWindowsPath = "$PSScriptRoot\..\wsl\setup.bash" | Resolve-Path
	$wslSetupScriptWslPath = wsl -d Ubuntu -e bash -c "wslpath -au '$wslSetupScriptWindowsPath'"
	wsl -d Ubuntu -e $wslSetupScriptWslPath
	if ($LASTEXITCODE -ne 0) {
		throw "WSL setup failed."
	}

	Write-SuccessMsg "`nPart 2 (Final) complete."
	Write-SuccessMsg 'Once restarted, check the ''README.md'' for the next steps.'
	Write-AttentionMsg 'Press Enter to restart the computer.'
	$null = Read-Host
	Restart-Computer
} catch {
	Write-ErrorMsg "$($_.Exception.Message)`nCheck the log for details: '$LOG_PATH'."
	exit 1
} finally {
	if ($shutdownBlocker) {
		Stop-Job $shutdownBlocker -ErrorAction SilentlyContinue
		Remove-Job $shutdownBlocker -ErrorAction SilentlyContinue
	}

	Stop-Transcript
}
