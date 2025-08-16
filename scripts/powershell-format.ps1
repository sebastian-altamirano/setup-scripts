#!/usr/bin/env pwsh

<#
.SYNOPSIS
Formats PowerShell files.

.PARAMETER Path
Specifies the path(s) to the PowerShell file(s) to format.
#>
param (
	[Parameter(Mandatory)]
	[ValidateNotNullOrEmpty()]
	[string[]] $Path
)


$CodeFormatting = Join-Path `
	-Path $PSScriptRoot `
	-ChildPath '..' `
	-AdditionalChildPath 'CodeFormatting.psd1' `
	-Resolve

foreach ($filePath in $Path) {
	$scriptContent = Get-Content -Path $filePath -Raw
	$formattedScriptContent = Invoke-Formatter -Settings $CodeFormatting -ScriptDefinition $scriptContent
	# Workaround for https://github.com/PowerShell/PSScriptAnalyzer/issues/775
	# (`Invoke-Formatter` does not have a `-Path` parameter).
	Set-Content -Force -NoNewline -Path $filePath -Value $formattedScriptContent
}
