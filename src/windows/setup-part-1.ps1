# Windows Setup - Part 1.
# Run this after a clean Windows installation.
# Requires restart.

#Requires -RunAsAdministrator

# Import utility functions.
. "$PSScriptRoot\utils.ps1"

$ErrorActionPreference = 'Stop'

$LogPath = Join-Path $PSScriptRoot 'windows-setup-part-1.log'
Start-Transcript -Path $LogPath -Append

try {
	Write-InfoMsg '===== Windows Setup - Part 1 ====='
	Write-AttentionMsg (
		"This script performs some preparatory tasks before continuing with the main installation.`n"
	)

	# Upgrade PowerShell early to avoid compatibility issues in later scripts.
	Write-InfoMsg 'Upgrading PowerShell...'
	winget install --exact --id Microsoft.PowerShell `
		--accept-package-agreements --accept-source-agreements `
		--silent
	Assert-LastExitCode 'Installing Microsoft.PowerShell with WinGet'

	Write-InfoMsg 'Enabling Hyper-V (required for WSL)...'
	Enable-WindowsOptionalFeature -Online -FeatureName Microsoft-Hyper-V -All -NoRestart

	Write-SuccessMsg "`nPart 1 complete."
	Write-SuccessMsg 'Once restarted, run ''setup-part-2.ps1'' to complete the setup.'
	Write-AttentionMsg 'Press Enter to restart the computer.'
	$null = Read-Host
	Restart-Computer
} catch {
	Write-ErrorMsg "$($_.Exception.Message)`nCheck the log for details: '$LogPath'."
	exit 1
} finally {
	Stop-Transcript
}
