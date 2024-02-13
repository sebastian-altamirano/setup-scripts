@{
	ExcludeRules = @()

	Rules        = @{
		PSUseCompatibleSyntax = @{
			Enable         = $true
			TargetVersions = @(
				'7.4'
			)
		}
	}
}
