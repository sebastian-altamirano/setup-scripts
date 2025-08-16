#!/usr/bin/env pwsh

<#
.SYNOPSIS
Lints PowerShell files.

.PARAMETER Path
Specifies the path(s) to the PowerShell file(s) to lint.
#>
param (
	[Parameter(Mandatory)]
	[ValidateNotNullOrEmpty()]
	[string[]] $Path
)


$PSScriptAnalyzerSettings = Join-Path `
	-Path $PSScriptRoot `
	-ChildPath '..' `
	-AdditionalChildPath 'PSScriptAnalyzerSettings.psd1' `
	-Resolve

foreach ($filePath in $Path) {
	Invoke-ScriptAnalyzer -Path $filePath -Settings $PSScriptAnalyzerSettings
}

