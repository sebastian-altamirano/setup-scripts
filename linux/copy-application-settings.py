from json import load as readJson
from os import makedirs as createDirectories
from os.path import abspath as getAbsolutePath
from shutil import copy2 as copyFile

SETTINGS_PATHS_KEY = "settingsPaths"

config = readJson("settings.json")

if SETTINGS_PATHS_KEY not in config:
	return

for resourceName, destination in config[SETTINGS_PATHS_KEY].values():
	absoluteDestination = getAbsolutePath(destination)
	createDirectories(absoluteDestination, exist_ok=True)
	copyFile(
		src=getAbsolutePath(f"app-settings/{resourceName}"),
		dst=absoluteDestination
	)
