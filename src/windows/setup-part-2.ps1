# Windows Setup - Part 2 (Final).
# Runs automatically after Part 1.
# Requires restart.

#Requires -RunAsAdministrator

# Import utility functions.
. "$PSScriptRoot\utils.ps1"

$ConfigPath = Join-Path $PSScriptRoot '..\..\config' | Resolve-Path

$ErrorActionPreference = 'Stop'

$LogPath = Join-Path $PSScriptRoot 'windows-setup-part-2.log'
Start-Transcript -Path $LogPath -Append

try {
	Write-InfoMsg '===== Windows Setup - Part 2 (Final) ====='
	Write-AttentionMsg (
		"The script will install many applications and may require your attention. " +
		"Please do not leave your computer unattended.`n"
	)

	# Workaround for https://github.com/microsoft/winget-cli/issues/229:
	# Starts a background job to abort shutdowns triggered by some installers.
	# This helps prevent unexpected restarts, but will not catch all cases.
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
		'9P1J8S7CCWWT', # Microsoft Clipchamp
		'9NBLGGH5R558', # Microsoft To Do
		'9NMPJ99VJBWV', # Phone Link
		'9NFTCH6J7FHV', # Power Automate
		'9P7BP5VNWKX5', # Quick Assist
		'9PC1H9VN18CM'  # Start Experiences App
	)
	foreach ($package in $winGetPackages) {
		winget uninstall --exact --id $package --accept-source-agreements --silent
	}
	taskkill /f /im OneDrive.exe
	# OneDrive uninstall returns error code 2147747483, but completes successfully and does not cause
	# the script to enter the catch block.
	winget uninstall 'OneDriveSetup.exe' --accept-source-agreements --silent

	# Package manager policy:
	# - Prefer WinGet for application installs.
	# - If something is not available in WinGet, use Chocolatey as a fallback.
	# - Do not use Scoop: these scripts run elevated, and Scoop is not designed to run/install cleanly
	#   from an administrative context.
	Write-InfoMsg 'Installing WinGet packages...'
	Write-InfoMsg 'Note that some applications might open during installation.'
	$winGetPackages = @(
		'ArminOsaj.AutoDarkMode',
		'Discord.Discord',
		'FlawlessWidescreen.FlawlessWidescreen',
		'Guru3D.Afterburner',
		'JanDeDobbeleer.OhMyPosh',
		'KDE.Krita',
		'M2Team.NanaZip',
		'Meta.Oculus',
		'Microsoft.PowerToys',
		'Microsoft.VCRedist.2010.x64',  # Required by FlawlessWidescreen
		'Microsoft.VisualStudioCode',
		'mtkennerly.ludusavi',
		'OBSProject.OBSStudio',
		'Philips.HueSync',
		'REALiX.HWiNFO',
		'Reshade.Setup.AddonsSupport',
		'Valve.Steam',
		# Microsoft Store apps:
		'9N0866FS04W8',   # Dolby Access
		'9N33VZK3C7TH',   # ImageGlass
		'9P30LSR4705L',   # LosslessCut
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
	Copy-Item "$ConfigPath\omp\ys-custom.omp.json" "$env:UserProfile\ys-custom.omp.json"

	Write-InfoMsg 'Copying Oh My Posh theme toggle script...'
	$pwshScriptsPath = "$([Environment]::GetFolderPath('MyDocuments'))\PowerShell\Scripts"
	New-Item -ItemType Directory -Path $pwshScriptsPath -Force | Out-Null
	Copy-Item "$ConfigPath\pwsh\Scripts\update-omp-theme.ps1" "$pwshScriptsPath\update-omp-theme.ps1"
	Unblock-File "$pwshScriptsPath\update-omp-theme.ps1"

	Write-InfoMsg 'Copying Auto Dark Mode settings...'
	$autoDarkModeSettingsPath = "$env:AppData\AutoDarkMode"
	New-Item -ItemType Directory -Path $autoDarkModeSettingsPath -Force | Out-Null
	Copy-Item "$ConfigPath\adm\config.yaml" "$autoDarkModeSettingsPath\config.yaml"
	Copy-Item "$ConfigPath\adm\scripts.yaml" "$autoDarkModeSettingsPath\scripts.yaml"

	Write-InfoMsg 'Copying PowerShell profile...'
	New-Item -ItemType Directory -Path (Split-Path $PROFILE) -Force | Out-Null
	Copy-Item "$ConfigPath\pwsh\Microsoft.PowerShell_profile.ps1" $PROFILE
	Unblock-File $PROFILE

	Write-InfoMsg 'Copying VS Code settings...'
	$vsCodeSettingsPath = "$env:AppData\Code\User"
	New-Item -ItemType Directory -Path $vsCodeSettingsPath -Force | Out-Null
	Copy-Item "$ConfigPath\vscode\settings.json" "$vsCodeSettingsPath\settings.json"
	Copy-Item "$ConfigPath\vscode\keybindings.json" "$vsCodeSettingsPath\keybindings.json"

	Write-InfoMsg 'Copying Windows Terminal settings...'
	$wtSettingsPath = "$env:LocalAppData\Packages\Microsoft.WindowsTerminal_8wekyb3d8bbwe\LocalState"
	New-Item -ItemType Directory -Path $wtSettingsPath -Force | Out-Null
	Copy-Item "$ConfigPath\wt\settings.json" "$wtSettingsPath\settings.json"

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
	Write-ErrorMsg "$($_.Exception.Message)`nCheck the log for details: '$LogPath'."
	exit 1
} finally {
	if ($shutdownBlocker) {
		Stop-Job $shutdownBlocker -ErrorAction SilentlyContinue
		Remove-Job $shutdownBlocker -ErrorAction SilentlyContinue
	}

	Stop-Transcript
}
