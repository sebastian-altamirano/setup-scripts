# Windows Setup - Part 1.
# Run this after a clean Windows installation.
# Requires restart.

#Requires -RunAsAdministrator


# Import utility functions.
. "$PSScriptRoot\utils.ps1"


$ErrorActionPreference = 'Stop'
trap {
	Write-ErrorMsg 'An error occurred. Check the log for details.'
	Stop-Transcript
	exit 1
}

Start-Transcript -Path "$PSScriptRoot\setup-part-1.log" -Append

Write-InfoMsg '===== Windows Dotfiles Setup - Part 1 ====='
Write-AttentionMsg "This script performs some preparatory tasks before continuing with the main installation.`n"

# Upgrade PowerShell early to avoid compatibility issues in later scripts.
Write-InfoMsg 'Upgrading PowerShell...'
winget install --exact --id Microsoft.PowerShell --accept-package-agreements --accept-source-agreements --silent

Write-InfoMsg 'Enabling Hyper-V (required for WSL)...'
Enable-WindowsOptionalFeature -Online -FeatureName Microsoft-Hyper-V -All

Write-InfoMsg 'Creating scheduled task for Part 2 (Final)...'
$action = New-ScheduledTaskAction -Execute 'pwsh' -Argument "-File `"$PSScriptRoot\setup-part-2.ps1`""
$trigger = New-ScheduledTaskTrigger -AtStartup
$principal = New-ScheduledTaskPrincipal -UserId 'SYSTEM' -LogonType ServiceAccount -RunLevel Highest
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries
Register-ScheduledTask -TaskName 'DotfilesSetupPart2' -Action $action -Trigger $trigger -Principal $principal -Settings $settings -Force

Write-SuccessMsg "`nPart 1 complete."
Write-SuccessMsg 'Once restarted, Part 2 (Final) will start automatically to complete the setup.'
Write-AttentionMsg 'Press Enter to restart the computer.'
$null = Read-Host
Stop-Transcript
Restart-Computer
