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

$shutdownBlocker = $null

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

	Write-InfoMsg 'Uninstalling bundled UWP applications...'
	$uwpPackages = @(
		'BingNews',
		'FeedbackHub',
		'Microsoft.Copilot',
		'MicrosoftSolitaireCollection',
		'MicrosoftStickyNotes',
		'Outlook'
	)
	foreach ($package in $uwpPackages) {
		try {
			Get-AppxPackage -All "*$package*" | Remove-AppxPackage -AllUsers
		} catch {
			Write-AttentionMsg "Could not uninstall UWP package '$package': $($_.Exception.Message)"
		}
	}

	Write-InfoMsg 'Uninstalling bundled WinGet applications...'
	$winGetUninstallArgs = @(
		'--accept-source-agreements',
		'--silent'
	)
	$winGetUninstallIds = @(
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
	foreach ($package in $winGetUninstallIds) {
		winget uninstall --exact --id $package @winGetUninstallArgs
		if ($LASTEXITCODE -ne 0) {
			Write-AttentionMsg "Could not uninstall WinGet package '$package': exit code $LASTEXITCODE."
		}
	}

	Stop-Process -Name OneDrive -Force -ErrorAction SilentlyContinue
	winget uninstall 'OneDriveSetup.exe' @winGetUninstallArgs
	if ($LASTEXITCODE -eq 2147747483) {
		Write-AttentionMsg (
			"OneDrive reported an incomplete uninstall (exit code $LASTEXITCODE), but it may have been " +
			"removed successfully."
		)
	} elseif ($LASTEXITCODE -ne 0) {
		Write-AttentionMsg "Could not uninstall OneDrive: exit code $LASTEXITCODE."
	}

	# Package manager policy:
	# - Prefer WinGet for application installs.
	# - If a package is unavailable in WinGet, use Chocolatey as a fallback.
	# - Avoid Scoop in this bootstrap: the entire script runs elevated, while Scoop is intended
	#   primarily for per-user, non-elevated installations.
	# - For WinGet packages whose installers reject an elevated context, use an equivalent Microsoft
	#   Store or Chocolatey package when available.
	Write-InfoMsg 'Installing WinGet packages...'
	Write-InfoMsg 'Note that some applications might open during installation.'
	$winGetInstallArgs = @(
		'--accept-package-agreements',
		'--accept-source-agreements',
		'--silent'
	)
	$winGetInstallIds = @(
		'AprilNEA.OpenLogi',
		'ArminOsaj.AutoDarkMode',
		'chocolatey.chocolatey',
		'cjpais.Handy',
		'Discord.Discord',
		'FlawlessWidescreen.FlawlessWidescreen',
		'JanDeDobbeleer.OhMyPosh',
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
		'Upscayl.Upscayl',
		'Valve.Steam',
		# Microsoft Store apps:
		'9PLM9XGG6VKS',   # ChatGPT
		'9N0866FS04W8',   # Dolby Access
		'9N33VZK3C7TH',   # ImageGlass
		'9P30LSR4705L',   # LosslessCut
		'XPDDT99J9GKB5C', # Samsung Magician
		'9NCBCSZSJRSB',   # Spotify ('Spotify.Spotify' installer cannot be run from an administrator context)
		'9MV0B5HZVK9Z',   # Xbox
		'9NBLGGH30XJ3'    # Xbox Accessories
	)
	foreach ($package in $winGetInstallIds) {
		winget install --exact --id $package @winGetInstallArgs
		Assert-LastExitCode "Installing WinGet package '$package'"
	}

	Write-InfoMsg 'Installing Chocolatey packages...'
	$chocoExecutable = Join-Path $env:ProgramData 'chocolatey\bin\choco.exe'
	$chocoInstallPackages = @(
		'equalizerapo'
	)
	foreach ($package in $chocoInstallPackages) {
		& $chocoExecutable install $package --yes
		Assert-LastExitCode "Installing Chocolatey package '$package'"
	}

	Write-InfoMsg 'Installing fonts...'
	# Refresh PATH to ensure `oh-my-posh` is available.
	$env:Path = [System.Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + `
		[System.Environment]::GetEnvironmentVariable("Path", "User")
	oh-my-posh font install monaspace
	Assert-LastExitCode 'Installing the Monaspace font with Oh My Posh'

	Write-InfoMsg 'Installing PowerShell modules...'
	Set-PSRepository -Name 'PSGallery' -InstallationPolicy Trusted
	Install-Module -Name z

	Write-InfoMsg 'Installing VS Code extensions...'
	$extensions = @(
		'GitHub.github-vscode-theme',
		'jgclark.vscode-todo-highlight',
		'ms-vscode-remote.remote-wsl',
		'YoavBls.pretty-ts-errors'
	)
	foreach ($extension in $extensions) {
		code --install-extension $extension
		Assert-LastExitCode "Installing VS Code extension '$extension'"
	}

	Write-InfoMsg 'Copying configuration files...'

	Write-InfoMsg 'Installing RNNoise VST plugin for Equalizer APO...'
	$equalizerApoPath = Join-Path $env:ProgramFiles 'EqualizerAPO'
	$equalizerApoConfigPath = Join-Path $equalizerApoPath 'config'
	$rnnoiseArchiveUri = 'https://github.com/werman/noise-suppression-for-voice/releases/latest/download/win-rnnoise.zip'
	$rnnoiseTemporaryPath = Join-Path ([System.IO.Path]::GetTempPath()) "win-rnnoise-$([guid]::NewGuid())"
	$rnnoiseArchivePath = Join-Path $rnnoiseTemporaryPath 'win-rnnoise.zip'
	$rnnoiseExtractPath = Join-Path $rnnoiseTemporaryPath 'extracted'
	$rnnoiseTargetPath = Join-Path $equalizerApoPath 'VSTPlugins\rnnoise_mono.dll'
	try {
		New-Item -ItemType Directory -Path $rnnoiseTemporaryPath -Force | Out-Null
		Invoke-WebRequest -Uri $rnnoiseArchiveUri -OutFile $rnnoiseArchivePath -ErrorAction Stop
		Expand-Archive -LiteralPath $rnnoiseArchivePath -DestinationPath $rnnoiseExtractPath
		$rnnoisePluginPath = Join-Path $rnnoiseExtractPath 'win-rnnoise\vst\rnnoise_mono.dll'
		if (-not (Test-Path -LiteralPath $rnnoisePluginPath -PathType Leaf)) {
			throw "The RNNoise archive does not contain the expected plugin: $rnnoisePluginPath"
		}

		Copy-Item $rnnoisePluginPath $rnnoiseTargetPath -Force
	} finally {
		Remove-Item -LiteralPath $rnnoiseTemporaryPath -Recurse -Force -ErrorAction SilentlyContinue
	}

	Write-InfoMsg 'Copying Equalizer APO settings...'
	Copy-Item "$ConfigPath\equalizer-apo\config.txt" (Join-Path $equalizerApoConfigPath 'config.txt') -Force

	Write-InfoMsg 'Copying Oh My Posh theme...'
	$ompThemeName = 'ys-custom.omp.json'
	Copy-Item "$ConfigPath\omp\$ompThemeName" "$env:UserProfile\$ompThemeName"

	Write-InfoMsg 'Copying Oh My Posh theme toggle script...'
	$pwshScriptsPath = "$([Environment]::GetFolderPath('MyDocuments'))\PowerShell\Scripts"
	$ompThemeToggleScriptName = 'update-omp-theme.ps1'
	New-Item -ItemType Directory -Path $pwshScriptsPath -Force | Out-Null
	Copy-Item "$ConfigPath\pwsh\Scripts\$ompThemeToggleScriptName" "$pwshScriptsPath\$ompThemeToggleScriptName"
	Unblock-File "$pwshScriptsPath\$ompThemeToggleScriptName"

	Write-InfoMsg 'Copying Auto Dark Mode settings...'
	$autoDarkModeSettingsPath = "$env:AppData\AutoDarkMode"
	$autoDarkModeConfigName = 'config.yaml'
	$autoDarkModeScriptsName = 'scripts.yaml'
	New-Item -ItemType Directory -Path $autoDarkModeSettingsPath -Force | Out-Null
	Copy-Item "$ConfigPath\adm\$autoDarkModeConfigName" "$autoDarkModeSettingsPath\$autoDarkModeConfigName"
	Copy-Item "$ConfigPath\adm\$autoDarkModeScriptsName" "$autoDarkModeSettingsPath\$autoDarkModeScriptsName"

	Write-InfoMsg 'Copying PowerShell profile...'
	New-Item -ItemType Directory -Path (Split-Path $PROFILE) -Force | Out-Null
	Copy-Item "$ConfigPath\pwsh\Microsoft.PowerShell_profile.ps1" $PROFILE
	Unblock-File $PROFILE

	Write-InfoMsg 'Copying VS Code settings...'
	$vsCodeSettingsPath = "$env:AppData\Code\User"
	$vsCodeSettingsName = 'settings.json'
	$vsCodeKeybindingsName = 'keybindings.json'
	New-Item -ItemType Directory -Path $vsCodeSettingsPath -Force | Out-Null
	Copy-Item "$ConfigPath\vscode\$vsCodeSettingsName" "$vsCodeSettingsPath\$vsCodeSettingsName"
	Copy-Item "$ConfigPath\vscode\$vsCodeKeybindingsName" "$vsCodeSettingsPath\$vsCodeKeybindingsName"

	Write-InfoMsg 'Copying Windows Terminal settings...'
	$wtSettingsPath = "$env:LocalAppData\Packages\Microsoft.WindowsTerminal_8wekyb3d8bbwe\LocalState"
	$wtSettingsName = 'settings.json'
	New-Item -ItemType Directory -Path $wtSettingsPath -Force | Out-Null
	Copy-Item "$ConfigPath\wt\$wtSettingsName" "$wtSettingsPath\$wtSettingsName"

	$wslDistroName = 'Ubuntu'
	Write-InfoMsg "Installing $wslDistroName in WSL..."
	wsl --install -d $wslDistroName --no-launch
	Assert-LastExitCode "Installing WSL distribution '$wslDistroName'"
	Write-InfoMsg "The $wslDistroName installer will prompt you to create a user and set a password."
	ubuntu.exe install
	Assert-LastExitCode "Initializing WSL distribution '$wslDistroName'"

	Write-InfoMsg 'Running WSL setup script...'
	$wslSetupScriptWindowsPath = "$PSScriptRoot\..\wsl\setup.bash" | Resolve-Path
	$wslSetupScriptWslPath = wsl -d $wslDistroName -e bash -c "wslpath -au '$wslSetupScriptWindowsPath'"
	Assert-LastExitCode "Resolving the WSL setup path for distribution '$wslDistroName'"
	wsl -d $wslDistroName -e $wslSetupScriptWslPath
	Assert-LastExitCode "Running the WSL setup for distribution '$wslDistroName'"

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
