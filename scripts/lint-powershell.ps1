#!/usr/bin/env pwsh

<#
.SYNOPSIS
Lints PowerShell scripts.

.PARAMETER Path
Specifies the path(s) to the PowerShell files or directories to lint. If a directory path is
provided, all PowerShell files in that directory and its subdirectories will be included.
.PARAMETER SettingsPath
Specifies the path to the file containing the linting rules.
#>
param (
	[Parameter(Mandatory)]
	[ValidateNotNullOrEmpty()]
	[string[]] $Path,
	[ValidateNotNullOrEmpty()]
	[string] $SettingsPath
)

Foreach ($scriptOrDirectoryPath in $Path) {
	If ($SettingsPath) {
		Invoke-ScriptAnalyzer -Path $scriptOrDirectoryPath -Settings $SettingsPath
	} Else {
		Invoke-ScriptAnalyzer -Path $scriptOrDirectoryPath
	}
}
