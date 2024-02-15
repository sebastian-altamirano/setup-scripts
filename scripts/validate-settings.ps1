#!/usr/bin/env pwsh

$configDirectoryPath = Join-Path -Path $PSScriptRoot -ChildPath ".." -AdditionalChildPath "config" -Resolve
$settingsFilePath = Join-Path -Path $configDirectoryPath -ChildPath "settings.json"
$settingsSchemaFilePath = Join-Path -Path $configDirectoryPath -ChildPath "settings.schema.json"

if (!(Test-Json -Path $settingsFilePath -SchemaFile $settingsSchemaFilePath)) {
	throw 'Failed to validate `settings.json` with `settings.schema.json`.'
}
