@{
	ModuleVersion        = '1.0.0'
	PowerShellVersion    = '7.4.1'
	GUID                 = '559886f2-b4c6-47ba-b4ed-530bc1099bfd'
	Author               = 'Sebastián Altamirano'
	Description          = 'Contains utility functions to be used by the Windows dotfiles.'
	RequiredModules      = @('ScheduledTasks')
	RootModule           = 'Utils.psm1'
	FunctionsToExport    = @(
		'Copy-Resource',
		'Install-ScoopPackage',
		'Register-ScriptExecution',
		'Unregister-ScriptExecution',
		'Start-Logging',
		'Stop-Logging'
	)
	CmdletsToExport      = @()
	VariablesToExport    = @()
	AliasesToExport      = @()
	DefaultCommandPrefix = 'Dotfiles'
}
