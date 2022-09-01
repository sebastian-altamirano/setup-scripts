from json import load as readJson
from subprocess import run

VSCODE_EXTENSIONS_KEY = "vscodeExtensions"

config = readJson("settings.json")

if VSCODE_EXTENSIONS_KEY not in config:
	return

for extension in config[VSCODE_EXTENSIONS_KEY]:
	run(["code", "--install-extension", extension])
