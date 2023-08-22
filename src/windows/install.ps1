#Requires -RunAsAdministrator

winget install `
	--exact --id --silent --accept-package-agreements --accept-source-agreements `
	Microsoft.PowerShell

pwsh .\install-part-1.ps1
