#!/usr/bin/env pwsh

$settingsPath = Join-Path -Path $PSScriptRoot -ChildPath ".." -AdditionalChildPath "config", "settings.json" -Resolve
$settingsSchemaPath = Join-Path -Path $PSScriptRoot -ChildPath ".." -AdditionalChildPath "config", "settings.schema.json" -Resolve

if (!(Test-Json -Path $settingsPath  -SchemaFile $settingsSchemaPath)) {
	throw 'Failed to validate `settings.json` with `settings.schema.json`.'
}
