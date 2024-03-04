#Requires -RunAsAdministrator

param (
	[string] $LogFilePath = "$env:UserProfile\Documents\dotfiles_install-$(Get-Date -Format 'yyyy_MM_dd-HH_mm_ss').log"
)

$dotfilesModulePath = Join-Path -Path $PSScriptRoot -ChildPath Dotfiles
Import-Module $dotfilesModulePath

Write-Output 'Validating `settings.json`.'
$configDirectoryPath = Join-Path -Path $PSScriptRoot -ChildPath ".." -AdditionalChildPath "..", "config" -Resolve
$settingsFilePath = Join-Path -Path $configDirectoryPath -ChildPath "settings.json"
$settingsSchemaFilePath = Join-Path -Path $configDirectoryPath -ChildPath "settings.schema.json"
$windowsUserSettingsDirectoryPath = Join-Path -Path $configDirectoryPath -ChildPath "windows"
$ubuntuUserSettingsDirectoryPath = Join-Path -Path $configDirectoryPath -ChildPath "ubuntu"
if (
	!(Test-DotfilesConfiguration `
			-ShouldValidateUbuntu $false `
			-SettingsFilePath $settingsFilePath `
			-SettingsSchemaFilePath $settingsSchemaFilePath `
			-WindowsUserSettingsDirectoryPath $windowsUserSettingsDirectoryPath`
			-UbuntuUserSettingsDirectoryPath $ubuntuUserSettingsDirectoryPath
	)
) {
	throw 'Failed to validate the settings, fix the errors and try again.'
}

Start-DotfilesLogging $LogFilePath

Write-Output "Installing Dotfiles's PowerShell module."
Copy-DotfilesResource -Path $dotfilesModulePath -Destination "$env:ProgramFiles\PowerShell\Modules"

Write-Output "Enabling Hyper-V because it is required by WSL."
Enable-WindowsOptionalFeature -Online -FeatureName Microsoft-Hyper-V -All

Register-DotfilesScriptExecution `
	-Path (Join-Path -Path $PSScriptRoot -ChildPath install-part-2.ps1) `
	-ScriptArgs $LogFilePath `
	-TaskPath Dotfiles `
	-TaskName ResumeInstallation `
	-RunLevel Highest

Stop-DotfilesLogging

Restart-Computer
