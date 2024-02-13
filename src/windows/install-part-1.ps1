#Requires -RunAsAdministrator

param (
	[string] $LogFilePath = "$env:UserProfile\Documents\dotfiles_install-$(Get-Date -Format 'yyyy_MM_dd-HH_mm_ss').log"
)

Write-Output 'Validating `settings.json`.'
if (!(Test-Json -Path "../../config/settings.json" -SchemaFile "../../config/settings.schema.json")) {
	throw 'Failed to validate `settings.json` with `settings.schema.json`, fix the errors and try again.'
}

Import-Module ".\Dotfiles"

Start-DotfilesLogging $LogFilePath

Write-Output "Installing Dotfiles's PowerShell module."
Copy-DotfilesResource -Path "Dotfiles" -Destination "$env:ProgramFiles\PowerShell\Modules"

Write-Output "Enabling Hyper-V because it is required by WSL."
Enable-WindowsOptionalFeature -Online -FeatureName Microsoft-Hyper-V -All

Register-DotfilesScriptExecution `
	-Path "install-part-2.ps1" `
	-ScriptArgs $LogFilePath `
	-TaskPath Dotfiles `
	-TaskName ResumeInstallation `
	-RunLevel Highest

Stop-DotfilesLogging

Restart-Computer
