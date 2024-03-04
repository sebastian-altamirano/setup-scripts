function TestConfigurationResources {
	param (
		[Parameter(Mandatory)]
		[ValidateSet('windows', 'ubuntu')]
		[string] $Target,
		[Parameter(Mandatory)]
		[object[]] $SettingsPaths,
		[Parameter(Mandatory)]
		[string] $UserSettingsDirectoryPath
	)

	$resourceNames = [string[]]($SettingsPaths | ForEach-Object { $_.resourceName })

	$isConfigurationValid = $true
	for ($index = 0; $index -lt $resourceNames.Length; ++$index) {
		$resourcePath = Join-Path -Path $UserSettingsDirectoryPath -ChildPath $resourceNames[$index]

		if (!(Test-Path ($resourcePath))) {
			$isConfigurationValid = $false
			Write-Error "``/$($Target)/settingsPaths/$($index)`` is invalid, ``$($resourcePath)`` does not exist."
		}
	}

	return $isConfigurationValid
}

function TestUbuntuGitGpgKey {
	param (
		[Parameter(Mandatory)]
		[string] $PrivateKeyName,
		[Parameter(Mandatory)]
		[string] $UbuntuUserSettingsDirectoryPath
	)

	$privateKeyPath = Join-Path -Path $UbuntuUserSettingsDirectoryPath -ChildPath $PrivateKeyName

	if (!(Test-Path $privateKeyPath)) {
		Write-Error "``/ubuntu/git/gpg/privateKeyName`` is invalid, ``$($privateKeyPath)`` does not exist."
		return $false
	}

	return $true
}

function TestUbuntuGitSshKey {
	param (
		[Parameter(Mandatory)]
		[string] $PrivateKeyName,
		[Parameter(Mandatory)]
		[string] $PublicKeyName,
		[Parameter(Mandatory)]
		[string] $UbuntuUserSettingsDirectoryPath
	)

	$privateKeyPath = Join-Path -Path $UbuntuUserSettingsDirectoryPath -ChildPath $PrivateKeyName
	$publicKeyPath = Join-Path -Path $UbuntuUserSettingsDirectoryPath -ChildPath $PublicKeyName

	$isValid = $true
	if (!(Test-Path $privateKeyPath)) {
		Write-Error "``/ubuntu/git/ssh/privateKeyName`` is invalid, ``$($privateKeyPath)`` does not exist."
		$isValid = $false
	}
	if (!(Test-Path $publicKeyPath)) {
		Write-Error "``/ubuntu/git/ssh/publicKeyName`` is invalid, ``$($publicKeyPath)`` does not exist."
		$isValid = $false
	}

	return $isValid
}

<#
.SYNOPSIS
Checks if the dotfiles configuration file is valid and if all the resources mentioned in it exist.

.DESCRIPTION
Checks if the dotfiles configuration file is valid and if all the resources mentioned in it exist,
to test this the following checks are performed:
- Checks if the configuration file is valid using the JSON schema.
- Checks if the resources listed in `/windows/settingsPaths` exist.
If `-ShouldValidateUbuntu` is `$true` the following is also checked:
- Checks if the resources listed in `/ubuntu/settingsPaths` exist.
- Checks if the SSH keys listed in `/ubuntu/git/ssh/privateKeyName` and
`/ubuntu/git/ssh/publicKeyName` exist.
- Checks if the GPG key mentioned in `/ubuntu/git/gpg/privateKeyName` exists.

.PARAMETER ShouldValidateUbuntu
Specifies if the Ubuntu configuration should be validated.
.PARAMETER SettingsFilePath
Specifies the path to the settings file.
.PARAMETER SettingsSchemaFilePath
Specifies the path to the settings schema file.
.PARAMETER WindowsUserSettingsDirectoryPath
Specifies the path to the Windows user settings directory.
.PARAMETER UbuntuUserSettingsDirectoryPath
Specifies the path to the Ubuntu user settings directory.

.EXAMPLE
Test-Configuration `
	-ShouldValidateUbuntu $true `
	-SettingsFilePath '/home/sebastian/dotfiles/config/settings.json' `
	-SettingsSchemaFilePath '/home/sebastian/dotfiles/config/settings.schema.json' `
	-WindowsUserSettingsDirectoryPath '/home/sebastian/dotfiles/config/windows' `
	-UbuntuUserSettingsDirectoryPath '/home/sebastian/dotfiles/config/ubuntu'
#>
function Test-Configuration {
	param (
		[bool] $ShouldValidateUbuntu = $false,
		[string] $SettingsFilePath,
		[string] $SettingsSchemaFilePath,
		[string] $WindowsUserSettingsDirectoryPath,
		[string] $UbuntuUserSettingsDirectoryPath
	)

	$isConfigurationValid = $true

	if (!(Test-Json -Path $SettingsFilePath -SchemaFile $SettingsSchemaFilePath)) {
		$isConfigurationValid = $false
		Write-Error 'Failed to validate the settings using the JSON schema.'
	}

	$config = (Get-Content $SettingsFilePath | ConvertFrom-Json)

	# Validates if the resources listed in `/windows/settingsPaths` exist.
	$isConfigurationValid = (
		TestConfigurationResources `
			-Target 'windows' `
			-SettingsPaths $config.windows.settingsPaths `
			-UserSettingsDirectoryPath $WindowsUserSettingsDirectoryPath
	) -and $isConfigurationValid

	if ($ShouldValidateUbuntu) {
		# Validates if the resources listed in `/ubuntu/settingsPaths` exist.
		$isConfigurationValid = (
			TestConfigurationResources `
				-Target 'ubuntu' `
				-SettingsPaths $config.ubuntu.settingsPaths `
				-UserSettingsDirectoryPath $UbuntuUserSettingsDirectoryPath
		) -and $isConfigurationValid

		# Validates if the SSH and GPG keys listed in `/ubuntu/git` exist.
		if ($config.ubuntu.git.signingMethod -eq 'gpg') {
			$isConfigurationValid = (
				TestUbuntuGitGpgKey `
					-PrivateKeyName $config.ubuntu.git.gpg.privateKeyName `
					-UbuntuUserSettingsDirectoryPath $UbuntuUserSettingsDirectoryPath
			) -and $isConfigurationValid
		} elseif ($config.ubuntu.git.signingMethod -eq 'ssh') {
			$isConfigurationValid = (
				TestUbuntuGitSshKey `
					-PrivateKeyName $config.ubuntu.git.ssh.privateKeyName `
					-PublicKeyName $config.ubuntu.git.ssh.publicKeyName `
					-UbuntuUserSettingsDirectoryPath $UbuntuUserSettingsDirectoryPath
			) -and $isConfigurationValid
		}
	}

	return $isConfigurationValid
}
