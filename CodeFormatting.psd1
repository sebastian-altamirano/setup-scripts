# OTBS (https://github.com/PowerShell/PSScriptAnalyzer/blob/1.24.0/Engine/Settings/CodeFormattingOTBS.psd1),
# but using tabs instead of spaces.
@{
	IncludeRules = @(
		'PSPlaceOpenBrace',
		'PSPlaceCloseBrace',
		'PSUseConsistentWhitespace',
		'PSUseConsistentIndentation',
		'PSAlignAssignmentStatement',
		'PSUseCorrectCasing'
	)

	Rules        = @{
		PSPlaceOpenBrace           = @{
			Enable             = $true
			OnSameLine         = $true
			NewLineAfter       = $true
			IgnoreOneLineBlock = $true
		}

		PSPlaceCloseBrace          = @{
			Enable             = $true
			NewLineAfter       = $false
			IgnoreOneLineBlock = $true
			NoEmptyLineBefore  = $false
		}

		PSUseConsistentIndentation = @{
			Enable              = $true
			Kind                = 'tab'
			PipelineIndentation = 'IncreaseIndentationForFirstPipeline'
		}

		PSUseConsistentWhitespace  = @{
			Enable                                  = $true
			CheckInnerBrace                         = $true
			CheckOpenBrace                          = $true
			CheckOpenParen                          = $true
			CheckOperator                           = $true
			CheckPipe                               = $true
			CheckPipeForRedundantWhitespace         = $false
			CheckSeparator                          = $true
			CheckParameter                          = $false
			IgnoreAssignmentOperatorInsideHashTable = $true
		}

		PSAlignAssignmentStatement = @{
			Enable         = $true
			CheckHashtable = $true
		}

		PSUseCorrectCasing         = @{
			Enable = $true
		}
	}
}
