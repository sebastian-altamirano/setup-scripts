@{
ModuleVersion = "1.0.0"
CompatiblePSEditions = @("Core")
GUID = "559886f2-b4c6-47ba-b4ed-530bc1099bfd"
Author = "Sebastián Altamirano"
Description = "My personal collection of utility functions"
RequiredModules = @("ScheduledTasks")
RootModule = "Dotfiles.psm1"
FunctionsToExport = @(
	"Copy-Resource",
	"Register-ScriptExecution",
	"Unregister-ScriptExecution",
	"Set-WindowsTheme",
	"Start-Logging",
	"Stop-Logging",
	"Test-HourWithinRange"
)
CmdletsToExport = @()
VariablesToExport = @()
AliasesToExport = @()
DefaultCommandPrefix = "Dotfiles"
}
