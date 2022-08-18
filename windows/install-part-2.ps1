#Requires -RunAsAdministrator

Start-DotfilesLogging -Name "dotfiles-install"

Unregister-DotfilesScriptExecution -TaskPath Dotfiles -TaskName ResumeInstalation

Write-Output "Installing Ubuntu using WSL."
wsl --install -d Ubuntu

Register-DotfilesScriptExecution `
	-Path ".\install-part-3.psd1" `
	-TaskPath Dotfiles `
	-TaskName ResumeInstallation `
	-RunLevel Highest

Stop-DotfilesLogging

Restart-Computer
