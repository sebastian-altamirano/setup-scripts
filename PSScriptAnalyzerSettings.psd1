@{
	ExcludeRules = @('PSAvoidUsingInvokeExpression', 'PSAvoidUsingWriteHost')

	Rules        = @{
		PSUseCompatibleSyntax = @{
			Enable         = $true
			TargetVersions = @(
				'7.5'
			)
		}
	}
}
