#Requires -RunAsAdministrator

param (
	[Parameter(Mandatory)]
	[string] $LogFilePath
)

Start-DotfilesLogging $LogFilePath

Unregister-DotfilesScriptExecution -TaskPath Dotfiles -TaskName ResumeInstalation

$configPath = "..\..\config\windows"
$config = (Get-Content "..\..\config\settings.json" | ConvertFrom-Json).windows

Write-Output "Installing winget packages."
winget import --accept-package-agreements --accept-source-agreements "$configPath\winget-packages.json"

Write-Output "Installing Scoop."
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
Invoke-RestMethod -Uri https://get.scoop.sh | Invoke-Expression

Write-Output "Installing Scoop packages."
Foreach ($packagesConfig in $config.scoopPackages) {
	Foreach ($package in $packagesConfig.packages) {
		Install-DotfilesScoopPackage -Bucket $packagesConfig.bucket -Package $package
	}
}

Write-Output "Installing VSCode extensions."
Foreach ($extension in $config.vscodeExtensions) {
	code --install-extension $extension
}

Write-Output "Removing Cortana."
Get-AppxPackage -allusers Microsoft.549981C3F5F10 | Remove-AppxPackage

Write-Output "Creating folders and quick access links."
$quickAccess = New-Object -ComObject shell.application -Verbose
Foreach ($folderName in $config.quickAccessFolders) {
	$folderPath = Join-Path -Path $env:UserProfile -ChildPath "Documents" -AdditionalChildPath $folderName
	$quickAccess.Namespace($folderPath).Self.InvokeVerb("pintohome")
}

Write-Output "Importing application settings."
Foreach ($resourceMapping in $config.settingsPaths) {
	$path = Join-Path $configPath $resourceMapping.resourceName
	$destination = $ExecutionContext.InvokeCommand.ExpandString($resourceMapping.destination)
	Copy-DotfilesResource -Path $path -Destination $destination
}

Write-Output -BackgroundColor Green -ForegroundColor Black "Finished!"
Write-Output "Now there are some manual steps you need to perform:"
Foreach ($resourceMapping in $config.settingsPaths) {
	If ($resourceMapping.postInstallationInstructions) {
		Write-Output "- $($resourceMapping.postInstallationInstructions)"
	}
}
Foreach ($instruction in $config.postInstallationInstructions) {
	Write-Output "- $($instruction)"
}
Write-Output "- Restart your computer for these changes to take effect."

Stop-DotfilesLogging

Read-Host -Prompt "Press Enter to exit."
