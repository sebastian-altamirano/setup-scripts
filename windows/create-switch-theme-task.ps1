#Requires -RunAsAdministrator

$lightThemeHour = 8
$darkThemeHour = 18

$pwshExecutablePath = $(get-command pwsh).Path
$scriptPath = Join-Path "scheduled-tasks" "switch-theme.ps1" | Resolve-Path

$action = New-ScheduledTaskAction `
	-Execute "$pwshExecutablePath" `
	-Argument "-File $scriptPath -LightThemeHour $lightThemeHour -DarkThemeHour $darkThemeHour"

$SessionStateChangeTrigger = Get-CimClass `
	-ClassName MSFT_TaskSessionStateChangeTrigger `
	-Namespace Root/Microsoft/Windows/TaskScheduler:MSFT_TaskEventTrigger
$afterUnlockTrigger = New-CimInstance -CimClass $SessionStateChangeTrigger -ClientOnly
$afterUnlockTrigger.StateChange = 8
$afterUnlockTrigger.Enabled = $True 
$triggers = @(
	$(New-ScheduledTaskTrigger -Daily -At (Get-Date -Hour $lightThemeHour -Minute 0 -Second 0)),
	$(New-ScheduledTaskTrigger -Daily -At (Get-Date -Hour $darkThemeHour -Minute 0 -Second 0 )),
	$(New-ScheduledTaskTrigger -AtLogon)
	$afterUnlockTrigger
)

Register-ScheduledTask `
	-Action $action `
	-Trigger $triggers `
	-TaskName "SwitchTheme" `
	-Description "Changes the Windows theme depending on the time of the day."
