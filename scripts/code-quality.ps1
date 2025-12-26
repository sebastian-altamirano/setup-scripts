#!/usr/bin/env pwsh

<#
.SYNOPSIS
Formats or lints bash, fish or PowerShell files.

.PARAMETER Action
Specifies whether to 'format' or 'lint' the files.
.PARAMETER Type
Specifies the type of files: 'bash', 'fish', or 'powershell'.
.PARAMETER Path
Specifies the path(s) to the file(s) to process. If omitted, processes all matching files in the
project.
#>
param(
	[Parameter(Mandatory)]
	[ValidateSet('format', 'lint')]
	[string] $Action,

	[Parameter(Mandatory)]
	[ValidateSet('bash', 'fish', 'powershell')]
	[string] $Type,

	[string[]] $Path
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$ProjectRoot = Split-Path -Path $PSScriptRoot -Parent

function Get-ProjectFile([string[]] $Include) {
	Get-ChildItem -Path $ProjectRoot -Recurse -File -Include $Include |
		Where-Object { $_.FullName -notmatch '[\\/](\.git|node_modules)[\\/]' } |
		Select-Object -ExpandProperty FullName
}

function Format-PowerShellFile([string] $Path, [string] $Settings) {
	$content = Get-Content -Path $Path -Raw
	$formatted = Invoke-Formatter -Settings $Settings -ScriptDefinition $content
	# Workaround for https://github.com/PowerShell/PSScriptAnalyzer/issues/775
	# (`Invoke-Formatter` does not have a `-Path` parameter).
	Set-Content -Force -NoNewline -Path $Path -Value $formatted
}

$files = if ($Path) { $Path } else {
	switch ($Type) {
		'bash' { Get-ProjectFile -Include '*.bash' }
		'fish' { Get-ProjectFile -Include '*.fish' }
		'powershell' {
			$extensions = if ($Action -eq 'format') { '*.ps1', '*.psm1' } else { '*.ps1', '*.psd1', '*.psm1' }
			Get-ProjectFile -Include $extensions
		}
	}
}

$files = @($files)
if ($files.Count -eq 0) { exit 0 }

switch ("$Action|$Type") {
	'format|bash' { & shfmt -w @files }
	'lint|bash' { & shellcheck @files }
	'format|fish' { & fish_indent -w @files }
	'lint|fish' { Write-Host 'No fish linter configured; skipping.' -ForegroundColor Yellow }
	'format|powershell' {
		$settings = Join-Path $ProjectRoot 'CodeFormatting.psd1'
		foreach ($file in $files) { Format-PowerShellFile -Path $file -Settings $settings }
	}
	'lint|powershell' {
		$settings = Join-Path $ProjectRoot 'PSScriptAnalyzerSettings.psd1'
		foreach ($file in $files) { Invoke-ScriptAnalyzer -EnableExit -Path $file -Settings $settings }
	}
}
