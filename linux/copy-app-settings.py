from json import load as readJson
from os import makedirs as createDirectories
from os.path import abspath as getAbsolutePath
from shutil import copy2 as copyFile

APP_SETTINGS_PATH = "app-settings"

appSettingsMappings = readJson("config/settings-paths.json")["paths"]
for resourceName, destination in appSettingsMappings.values():
	absoluteDestination = getAbsolutePath(destination)
	createDirectories(absoluteDestination, exist_ok=True)
	copyFile(
		src=getAbsolutePath(f"{APP_SETTINGS_PATH}/{resourceName}"),
		dst=absoluteDestination
	)
