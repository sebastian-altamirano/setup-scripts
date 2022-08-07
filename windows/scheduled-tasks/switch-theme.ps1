param (
	[Parameter(Mandatory)]
	[ValidateRange(0, 23)]
	[Int32] $LightThemeHour,
	[Parameter(Mandatory)]
	[ValidateRange(0, 23)]
	[Int32] $DarkThemeHour
)

if (Test-DotfilesHourWithinRange -Start $LightThemeHour -End $DarkThemeHour) {
	Set-DotfilesWindowsTheme -Theme Light
} else {
	Set-DotfilesWindowsTheme -Theme Dark
}
