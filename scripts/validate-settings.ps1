#!/usr/bin/env pwsh

$dotfilesValidationModulePath = Join-Path `
	-Path $PSScriptRoot `
	-ChildPath '..' `
	-AdditionalChildPath 'src', 'windows', 'Dotfiles', 'Validation' `
	-Resolve
Import-Module $dotfilesValidationModulePath

$configDirectoryPath = Join-Path -Path $PSScriptRoot -ChildPath ".." -AdditionalChildPath "config" -Resolve
$settingsFilePath = Join-Path -Path $configDirectoryPath -ChildPath "settings.json"
$settingsSchemaFilePath = Join-Path -Path $configDirectoryPath -ChildPath "settings.schema.json"
$windowsUserSettingsDirectoryPath = Join-Path -Path $configDirectoryPath -ChildPath "windows"
$ubuntuUserSettingsDirectoryPath = Join-Path -Path $configDirectoryPath -ChildPath "ubuntu"

if (
	!(Test-DotfilesConfiguration `
			-ShouldValidateUbuntu $true `
			-SettingsFilePath $settingsFilePath `
			-SettingsSchemaFilePath $settingsSchemaFilePath `
			-WindowsUserSettingsDirectoryPath $windowsUserSettingsDirectoryPath `
			-UbuntuUserSettingsDirectoryPath $ubuntuUserSettingsDirectoryPath
	)
) {
	throw 'Failed to validate the settings, fix the errors and try again.'
}
