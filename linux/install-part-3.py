from json import load as readJson
from os import makedirs as createDirectories
from os.path import abspath as getAbsolutePath
from shutil import copy2 as copyFile
from subprocess import run

RED_BG_BLACK_FG = "\x1b[6;30;41m"
GREEN_BG_BLACK_FG = "\x1b[6;30;42m"
COLOR_TERMINATOR "\x1b[0m"

config = readJson("settings.json")

QUICK_ACCESS_FOLDERS_KEY = "quickAccessFolders"
SETTINGS_PATHS_KEY = "settingsPaths"
VSCODE_EXTENSIONS_KEY = "vscodeExtensions"

if QUICK_ACCESS_FOLDERS_KEY in config:
	print(
		f'{RED_BG_BLACK_FG}Settings contains a value for "{QUICK_ACCESS_FOLDERS_KEY}", '
		f"but this key is not supported for this OS.{COLOR_TERMINATOR}"
	)

if VSCODE_EXTENSIONS_KEY in config:
	# Install VSCode extensions.
	for extension in config[VSCODE_EXTENSIONS_KEY]:
		run(["code", "--install-extension", extension])

if SETTINGS_PATHS_KEY in config:
	postInstallationInstructions = [
		f"{GREEN_BG_BLACK_FG}Finished!{COLOR_TERMINATOR}"
		"Now there are some manual steps you need to perform:",
		"- Run `tide configure` to configure the aspect of fish.",
	]

	COMPLETION_COMMANDS_DESTINATION_KEY = "completionCommands"
	DESTINATION_KEY = "destination"
	POST_INSTALLATION_INSTRUCTIONS_KEY = "postInstallationInstructions"
	RESOURCE_NAME_KEY = "resourceName"

	# Copy application settings.
	for resourceMapping in config[SETTINGS_PATHS_KEY]:
		absoluteDestination = getAbsolutePath(resourceMapping[DESTINATION_KEY])
		createDirectories(absoluteDestination, exist_ok=True)
		copyFile(
			src=getAbsolutePath(f"app-settings/{resourceMapping[RESOURCE_NAME_KEY]}"),
			dst=absoluteDestination
		)

		if COMPLETION_COMMANDS_DESTINATION_KEY in resourceMapping:
			for commandArgs in resourceMapping[COMPLETION_COMMANDS_DESTINATION_KEY]:
				run(commandArgs)

		if POST_INSTALLATION_INSTRUCTIONS_KEY in resourceMapping:
			postInstallationInstructions.append(
				f"- {resourceMapping[POST_INSTALLATION_INSTRUCTIONS_KEY]}"
			)

	# Show post-installation instructions.
	for instruction in postInstallationInstructions:
		print(instruction)
