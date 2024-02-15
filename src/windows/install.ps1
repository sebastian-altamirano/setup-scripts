#Requires -RunAsAdministrator

Write-Output "Upgrading PowerShell."
winget install `
	--exact --id --silent --accept-package-agreements --accept-source-agreements `
	Microsoft.PowerShell

# Do not run anything in this script as it will most likely run in an outdated version of PowerShell
# (which may not support what you want to run), use `install-part-{1,2,3}.ps1` instead.

pwsh (Join-Path -Path $PSScriptRoot -ChildPath install-part-1.ps1)
