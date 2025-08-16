#!/usr/bin/env pwsh

<#
.SYNOPSIS
Lints all PowerShell files in the project.
#>


$projectRoot = Split-Path -Path $PSScriptRoot -Parent

[string[]]$files = Get-ChildItem -Path $projectRoot -Recurse -Include *.ps1, *.psd1, *.psm1 -File |
	Where-Object { $_.FullName -notmatch '\.git[\\/]' -and $_.FullName -notmatch 'node_modules[\\/]' } |
	Select-Object -ExpandProperty FullName

& "$PSScriptRoot/powershell-lint.ps1" -Path $files
