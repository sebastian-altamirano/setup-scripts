/// <reference types="lint-staged" />

/** @param {string} fileName */
function formatPowerShellScript(fileName) {
	return `scripts/format-powershell.ps1 \
-Path ${fileName} \
-SettingsPath src/windows/formatter-settings.psd1`;
}

/** @param {string} fileName */
function lintPowerShellScript(fileName) {
	return `scripts/lint-powershell.ps1 \
-Path ${fileName} \
-SettingsPath src/windows/linter-settings.psd1`;
}

/**
 * @type {import('lint-staged').Config}
 */
export default {
	"*.{code-workspace,json,md}": "prettier --write",
	"*.{mjs,js}": ["prettier --write", "eslint"],
	"*.psd1": (fileNames) => fileNames.map(formatPowerShellScript),
	"*.{ps1,psm1}": (fileNames) =>
		fileNames
			.map((fileName) => [formatPowerShellScript(fileName), lintPowerShellScript(fileName)])
			.flat(),

	"*.py": [
		"pdm run -p src/ubuntu black",
		"pdm run -p src/ubuntu isort",
		"pdm run -p src/ubuntu mypy",
		"pdm run -p src/ubuntu pylint",
		"pdm run -p src/ubuntu unittest",
	],
};
