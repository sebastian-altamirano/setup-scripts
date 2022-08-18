#Requires -RunAsAdministrator

Import-Module ".\Dotfiles"

Start-DotfilesLogging -Name "dotfiles-install"

Write-Output "Installing Dotfiles's PowerShell module."
Copy-DotfilesResource -Path ".\Dotfiles" -Destination "$env:ProgramFiles\PowerShell\Modules"

Write-Output "Enabling Hyper-V because it is required by WSL."
Enable-WindowsOptionalFeature -Online -FeatureName Microsoft-Hyper-V -All

Register-DotfilesScriptExecution `
	-Path ".\install-part-2.psd1" `
	-TaskPath Dotfiles `
	-TaskName ResumeInstallation `
	-RunLevel Highest

Stop-DotfilesLogging

Restart-Computer
