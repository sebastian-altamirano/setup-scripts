function .. { Set-Location .. }
function ... { Set-Location ../.. }
function .... { Set-Location ../../.. }

New-Alias c Clear-Host
New-Alias e explorer

oh-my-posh init pwsh --config ys | Invoke-Expression
