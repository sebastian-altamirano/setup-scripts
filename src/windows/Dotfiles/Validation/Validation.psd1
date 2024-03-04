@{
	ModuleVersion        = '1.0.0'
	PowerShellVersion    = '7.4.1'
	GUID                 = '370273cf-6731-43f5-99ac-56ab24e527f8'
	Author               = 'Sebastián Altamirano'
	Description          = 'Contains functions that can be used to validate the dotfiles settings using any OS.'
	RequiredModules      = @()
	RootModule           = 'Validation.psm1'
	FunctionsToExport    = @(
		'Test-Configuration'
	)
	CmdletsToExport      = @()
	VariablesToExport    = @()
	AliasesToExport      = @()
	DefaultCommandPrefix = 'Dotfiles'
}
