#Requires -RunAsAdministrator

Start-DotfilesLogging -Name "dotfiles-install"

Unregister-DotfilesScriptExecution -TaskPath Dotfiles -TaskName ResumeInstalation

$configPath = ".\config"
$config = Get-Content "settings.json" | ConvertFrom-Json

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

Write-Host "Importing Windows settings."
reg import "$configPath\windows-settings.reg"

Write-Host "Importing application settings."
Foreach ($mapping in $config.settingsPaths) {
	$path = Join-Path ".\app-settings" $mapping.resourceName
	$destination = $ExecutionContext.InvokeCommand.ExpandString($mapping.destination)
	Copy-DotfilesResource -Path $path -Destination $destination
}

Write-Host "Creating scheduled tasks."
.\create-switch-theme-task.ps1

Write-Host "Downloading fonts."
$fontsZipPath = (Resolve-Path "JetBrainsMono.zip").Path
Invoke-WebRequest "https://fonts.google.com/download?family=JetBrains%20Mono" -OutFile $fontsZipPath
Expand-Archive $fontsZip -DestinationPath "fonts"

Write-Host -BackgroundColor Green "Finished!"
Write-Host "Now there are some manual steps you need to perform:"
Write-Host "- Install the fonts that have been downloaded to $fontsZipPath."
Write-Host "- Change the screen refresh rate to the maximum available value."

Stop-DotfilesLogging

Read-Host -Prompt "Press Enter to exit."
