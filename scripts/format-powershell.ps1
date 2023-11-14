#!/usr/bin/env pwsh

<#
.SYNOPSIS
Formats PowerShell scripts.

.PARAMETER Path
Specifies the path(s) to the PowerShell files or directories to format. If a directory path is
provided, all PowerShell files in that directory and its subdirectories will be included.
.PARAMETER SettingsPath
Specifies the path to the file containing the formatting rules.
#>
param (
	[Parameter(Mandatory)]
	[ValidateNotNullOrEmpty()]
	[string[]] $Path,
	[ValidateNotNullOrEmpty()]
	[string] $SettingsPath
)

<#
.SYNOPSIS
Formats PowerShell scripts using Invoke-Formatter.

.PARAMETER Path
Specifies the path to the file to be formatted.
.PARAMETER SettingsPath
Specifies the path to the file containing the formatting rules.
#>
function Format-Script {
	param (
		[Parameter(Mandatory)]
		[ValidateNotNullOrEmpty()]
		[string] $Path,
		[ValidateNotNullOrEmpty()]
		[string] $SettingsPath
	)

	$scriptContent = Get-Content -Path $Path -Raw

	If ($SettingsPath) {
		$formattedScriptContent = Invoke-Formatter -Settings $SettingsPath -ScriptDefinition $scriptContent
	} Else {
		$formattedScriptContent = Invoke-Formatter -ScriptDefinition $scriptContent
	}

	# Workaround for https://github.com/PowerShell/PSScriptAnalyzer/issues/775
	# (`Invoke-Formatter` does not have a `-Path` parameter).
	Set-Content -Force -NoNewline -Path $Path -Value $formattedScriptContent
}

<#
.SYNOPSIS
Gets the paths of PowerShell script files in a specified directory.

.PARAMETER Path
Specifies the directory path to search for PowerShell script files.
#>
function Get-ScriptPath {
	param (
		[Parameter(Mandatory)]
		[ValidateNotNullOrEmpty()]
		[string] $Path
	)

	return Get-ChildItem `
		-File `
		-Include "*.ps1", "*.psd1", "*.psm1" `
		-Path $Path `
		-Recurse `
	| Select-Object -ExpandProperty FullName
}


<#
.SYNOPSIS
Tests if a path is a directory.

.PARAMETER Path
Specifies the path to be tested.
#>
function Test-Directory {
	param (
		[Parameter(Mandatory)]
		[ValidateNotNullOrEmpty()]
		[string] $Path
	)

	return Test-Path -LiteralPath $Path -Type Container
}

Foreach ($scriptOrDirectoryPath in $Path) {
	If (Test-Directory -Path $scriptOrDirectoryPath) {
		$scriptPaths = Get-ScriptPath -Path $scriptOrDirectoryPath
		Foreach ($scriptPath in $scriptPaths) {
			Format-Script -Path $scriptPath -SettingsPath $SettingsPath
		}
	} else {
		Format-Script -Path $scriptOrDirectoryPath -SettingsPath $SettingsPath
	}
}
