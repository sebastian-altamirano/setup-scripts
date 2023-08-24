#Requires -RunAsAdministrator

param (
	[Parameter(Mandatory)]
	[string] $LogFilePath
)

Start-DotfilesLogging $LogFilePath

Unregister-DotfilesScriptExecution -TaskPath Dotfiles -TaskName ResumeInstalation

$configPath = "..\..\config\windows"
$config = (Get-Content "..\..\config\settings.json" | ConvertFrom-Json).windows

Write-Host "Installing winget packages."
winget import --accept-package-agreements --accept-source-agreements "$configPath\winget-packages.json"

Write-Host "Installing VSCode extensions."
Foreach ($extension in $config.vscodeExtensions) {
	code --install-extension $extension
}

Write-Host "Removing Cortana."
Get-AppxPackage -allusers Microsoft.549981C3F5F10 | Remove-AppxPackage

Write-Host "Creating folders and quick access links."
$quickAccess = New-Object -ComObject shell.application -Verbose
Foreach ($folderName in $config.quickAccessFolders) {
	$folderPath = Join-Path $env:UserProfile "Documents" $folderName
	$quickAccess.Namespace($folderPath).Self.InvokeVerb("pintohome")
}

Write-Host "Importing application settings."
Foreach ($resourceMapping in $config.settingsPaths) {
	$path = Join-Path $configPath $resourceMapping.resourceName
	$destination = $ExecutionContext.InvokeCommand.ExpandString($resourceMapping.destination)
	Copy-DotfilesResource -Path $path -Destination $destination

	if ($resourceMapping.completionCommands) {
		Foreach ($commandArgs in $resourceMapping.completionCommands) {
      ($commandArgs -Join " ")
			Invoke-Expression ($commandArgs -Join " ")
		}
	}
}

Write-Host "Downloading fonts."
$fontsZipPath = (Resolve-Path "JetBrainsMono.zip").Path
Invoke-WebRequest "https://fonts.google.com/download?family=JetBrains%20Mono" -OutFile $fontsZipPath
Expand-Archive $fontsZip -DestinationPath "fonts"

Write-Host -BackgroundColor Green -ForegroundColor Black "Finished!"
Write-Host "Now there are some manual steps you need to perform:"
Write-Host "- Install the fonts that have been downloaded to $fontsZipPath."
Foreach ($resourceMapping in $config.settingsPaths) {
	if ($resourceMapping.postInstallationInstructions) {
		Write-Host "- $($resourceMapping.postInstallationInstructions)"
	}
}
Foreach ($instruction in $config.postInstallationInstructions) {
	Write-Host "- $($instruction)"
}

Stop-DotfilesLogging

Read-Host -Prompt "Press Enter to exit."
