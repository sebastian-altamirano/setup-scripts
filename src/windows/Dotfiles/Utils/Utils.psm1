<#
.SYNOPSIS
Copies a file or directory recursively to another location, creating the target directory if it does
not exist.

.PARAMETER Path
Specifies the source path, it can be relative or absolute and can contain environment variables.
.PARAMETER Destination
Specifies the destination path, it can be relative or absolute and can contain environment
variables.

.EXAMPLE
Copy-DotfilesResource -Path settings.json -Destination $env:AppData\Code\User\settings.json
.EXAMPLE
Copy-DotfilesResource -Path Dotfiles -Destination $env:ProgramFiles\PowerShell\Modules
#>
function Copy-Resource {
	param (
		[Parameter(Mandatory)]
		[string] $Path,
		[Parameter(Mandatory)]
		[string] $Destination
	)

	New-Item -ItemType Directory -Force -Path $Destination | Out-Null
	Copy-Item -Path $Path -Destination $Destination -Recurse
}

<#
.SYNOPSIS
Installs a Scoop package.

.PARAMETER Package
Specifies the name package to install.
.PARAMETER Bucket
Specifies the bucket to which the package belongs. This parameter is optional, since it is not
necessary to install packages that belong to the main bucket.

.NOTES
The function requires Scoop to be installed and available in the system PATH.

.EXAMPLE
Install-DotfilesScoopPackage -Package "main/7zip"
.EXAMPLE
Install-DotfilesScoopPackage -Package "nerd-fonts/JetBrainsMono-NF" -Bucket "nerd-fonts"
#>
function Install-ScoopPackage {
	param (
		[Parameter(Mandatory)]
		[string] $Package,
		[string] $Bucket
	)

	If ($Bucket) {
		$addBucketResult = scoop bucket add $Bucket
		If ($addBucketResult -and $addBucketResult.StartsWith('Unknown bucket')) {
			# The bucket does not exist.
			Write-Error "Failed to install bucket '$Bucket'."
		} Elseif (-not (scoop install $Package)) {
			Write-Error "Failed to install package '$Package' from bucket '$Bucket'."
		}
	} Elseif (-not (scoop install $Package)) {
		Write-Error "Failed to install package '$Package'."
	}
}

<#
.SYNOPSIS
Registers an scheduled task to run a script at startup using pwsh.

.PARAMETER Path
Specifies the path of the script, it can be relative or absolute and can contain environment
variables.
.PARAMETER TaskName
Specifies the task name.
.PARAMETER TaskPath
Specifies the task namespace.
.PARAMETER RunLevel
Specifies the required privilege level to run the task.
.PARAMETER ScriptArgs
Specifies the arguments to be passed to the script.

.EXAMPLE
Register-DotfilesScriptExecution `
	-Path install-part-2.ps1 `
	-TaskPath Dotfiles `
	-TaskName ResumeInstallation `
	-RunLevel Highest
	-ScriptArgs "-LogFilePath $env:UserProfile\Documents\dotfiles-install.log"

.LINK
Unregister-DotfilesScriptExecution
#>
function Register-ScriptExecution {
	param (
		[Parameter(Mandatory)]
		[string] $Path,
		[Parameter(Mandatory)]
		[string] $TaskName,
		[string] $TaskPath = "",
		[Microsoft.PowerShell.Cmdletization.GeneratedTypes.ScheduledTask.RunLevelEnum] $RunLevel = "Limited",
		[string] $ScriptArgs = ""
	)

	$pwshExecutablePath = $(Get-Command pwsh).Path

	$action = New-ScheduledTaskAction `
		-Execute $pwshExecutablePath `
		-Argument "-File $(Resolve-Path $Path) $ScriptArgs"
	$trigger = New-ScheduledTaskTrigger -AtStartup

	Register-ScheduledTask `
		-Action $action `
		-Trigger $trigger	`
		-TaskName $TaskName `
		-TaskPath $TaskPath `
		-RunLevel $RunLevel
}

<#
.SYNOPSIS
Unregisters an scheduled task registered with Register-ScriptExecution.

.PARAMETER TaskName
Specifies the task name.
.PARAMETER TaskPath
Specifies the task namespace.

.EXAMPLE
Unregister-DotfilesScriptExecution -TaskPath Dotfiles -TaskName ResumeInstalation

.LINK
Register-DotfilesScriptExecution
#>
function Unregister-ScriptExecution {
	param (
		[Parameter(Mandatory)]
		[string] $TaskName,
		[string] $TaskPath = ""
	)

	Unregister-ScheduledTask -TaskName $TaskName -TaskPath $TaskPath
}

<#
.SYNOPSIS
Creates a record of all or part of a PowerShell session to a log file.

.DESCRIPTION
Creates a record of all or part of a PowerShell session to a log file.
If the file already exists, the record is appended to the end of the file.
Write-Output can be used to add comments.
If the command is executed inside a script, the path to the script will be logged.

.PARAMETER Path
Specifies the path where the log file will be saved, it can be relative or absolute and can contain
environment variables.

.EXAMPLE
Start-DotfilesLogging $env:UserProfile\Documents\dotfiles-install.log

.LINK
Stop-DotfilesLogging
#>
function Start-Logging {
	[CmdletBinding(SupportsShouldProcess)]
	param (
		[Parameter(Mandatory)]
		[string] $Path
	)

	Start-Transcript `
		-Path $Path `
		-UseMinimalHeader `
		-IncludeInvocationHeader `
		-Append `
		-WhatIf:$WhatIfPreference `
	| Out-Null
	if ($PSCommandPath) {
		Write-Output "--- Running $PSCommandPath ---"
	}
}

<#
.SYNOPSIS
Stops logging.

.LINK
Start-DotfilesLogging
#>
function Stop-Logging {
	Stop-Transcript
}
