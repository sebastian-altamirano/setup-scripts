#Requires -RunAsAdministrator

winget install `
	--exact --id --silent --accept-package-agreements --accept-source-agreements `
	Microsoft.PowerShell

if (!(Test-Json -Path "../../config/settings.json" -SchemaFile "../../config/settings.schema.json")) {
	throw 'Failed to validate `settings.json` with `settings.schema.json`, fix the errors and try again.'
}

pwsh .\install-part-1.ps1
