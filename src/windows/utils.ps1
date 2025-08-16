function Write-InfoMsg {
	param([string]$Message)
	Write-Host "Info: $Message" -ForegroundColor Cyan
}

function Write-AttentionMsg {
	param([string]$Message)
	Write-Host "Attention: $Message" -ForegroundColor Yellow
}

function Write-SuccessMsg {
	param([string]$Message)
	Write-Host "Success: $Message" -ForegroundColor Green
}

function Write-ErrorMsg {
	param([string]$Message)
	Write-Host "Error: $Message" -ForegroundColor Red
}
