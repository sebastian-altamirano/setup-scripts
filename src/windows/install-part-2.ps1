#Requires -RunAsAdministrator

param (
	[Parameter(Mandatory)]
	[string] $LogFilePath
)

Start-DotfilesLogging $LogFilePath

Unregister-DotfilesScriptExecution -TaskPath Dotfiles -TaskName ResumeInstalation

Write-Output "Installing Ubuntu using WSL."
wsl --install -d Ubuntu

Register-DotfilesScriptExecution `
	-Path "install-part-3.ps1" `
	-ScriptArgs $LogFilePath
	-TaskPath Dotfiles `
	-TaskName ResumeInstallation `
	-RunLevel Highest

Stop-DotfilesLogging

Restart-Computer
