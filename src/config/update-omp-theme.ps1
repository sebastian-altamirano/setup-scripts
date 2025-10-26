param(
	[string]$ConfigurationFile,
	[string]$Theme
)

$fileContent = Get-Content $ConfigurationFile -Raw | ConvertFrom-Json
$fileContent.palettes.template = $Theme
$fileContent | ConvertTo-Json -Depth 100 | Set-Content $ConfigurationFile
