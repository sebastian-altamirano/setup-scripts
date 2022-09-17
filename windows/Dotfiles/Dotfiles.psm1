<#
.SYNOPSIS
Copies a file or directory recursively to another location, creating the target directory if it
does not exist.

.PARAMETER Path
Specifies the source path.
.PARAMETER Destination
Specifies the destination path.

.EXAMPLE
Copy-DotfilesResource -Path "Dotfiles" -Destination $env:ProgramFiles\PowerShell\Modules
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
Registers an scheduled task to run a script at startup using pwsh.

.PARAMETER Path
Specifies the path of the script, can be relative or absolute.
.PARAMETER TaskName
Specifies the task name.
.PARAMETER TaskPath
Specifies the task namespace.
.PARAMETER RunLevel
Specifies the required privilege level to run the task.

.EXAMPLE
Register-DotfilesScriptExecution `
	-Path install-part-2.ps1 `
	-TaskPath Dotfiles `
	-TaskName ResumeInstallation `
	-RunLevel Highest

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
		[Microsoft.PowerShell.Cmdletization.GeneratedTypes.ScheduledTask.RunLevelEnum] $RunLevel = "Limited"
	)

	$pwshExecutablePath = $(Get-Command pwsh).Path

	$action = New-ScheduledTaskAction `
		-Execute $pwshExecutablePath `
		-Argument "-File $(Resolve-Path $Path)"
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
Changes the Windows theme.

.DESCRIPTION
Changes the Windows theme.
Your computer may slow down while applying the theme.

.PARAMETER Theme
Specifies the Windows theme to apply.

.EXAMPLE
Set-DotfilesWindowsTheme Dark
#>
function Set-WindowsTheme {
	param (
		[Parameter(Mandatory)]
		[ValidateSet("Light", "Dark")]
		[string] $Theme
	)

	$themePropertyPath = "HKCU:\Software\Microsoft\Windows\CurrentVersion\Themes\Personalize"
	$useLightTheme = $Theme -eq "Light"

	New-ItemProperty `
		-Path $themePropertyPath `
		-Name "SystemUsesLightTheme" `
		-Value $useLightTheme `
		-PropertyType DWORD `
		-Force `
		| Out-Null
	New-ItemProperty `
		-Path $themePropertyPath `
		-Name "AppsUseLightTheme" `
		-Value $useLightTheme `
		-PropertyType DWORD `
		-Force `
		| Out-Null
}

<#
.SYNOPSIS
Creates a record of all or part of a PowerShell session to a log file in the Documents directory.

.DESCRIPTION
Creates a record of all or part of a PowerShell session to a log file in the Documents directory.
If the file already exists, the record is appended to the end of the file.
Write-Host can be used to add comments.

.PARAMETER Name
Specifies the name of the log file.

.EXAMPLE
Start-DotfilesLogging dotfiles-install

.LINK
Stop-DotfilesLogging
#>
function Start-Logging {
	param (
		[Parameter(Mandatory)]
		[string] $Name
	)

	Start-Transcript `
		-Path "$env:UserProfile\Documents\$Name.log" `
		-UseMinimalHeader `
		-IncludeInvocationHeader `
		-Append `
		| Out-Null
	Write-Host (Get-Location).Path
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

<#
.SYNOPSIS
Checks if the current time is within the hour range [Start, End).

.PARAMETER Start
Specifies the hour at which the time range starts.
.PARAMETER End
Specifies the hour at which the time range ends.

.EXAMPLE
Test-DotfilesHourWithinRange -Start 9 -End 18
True  # If the time at which the script was executed is in the range [9-18).
.EXAMPLE
Test-DotfilesHourWithinRange -Start 18 -End 9
True  # If the time at which the script was executed is in the range [0-9) U [18-23].
#>
function Test-HourWithinRange {
	param (
		[Parameter(Mandatory)]
		[ValidateRange(0, 23)]
		[Int32] $Start,
		[Parameter(Mandatory)]
		[ValidateRange(0, 23)]
		[Int32] $End
	)

	$currentHour = (Get-Date).Hour

	if ($Start -lt $End) {
		return  $CurrentHour -ge $Start -and $CurrentHour -lt $End
	} else {
		return $CurrentHour -lt $End -and $CurrentHour -ge $Start
	}
}
