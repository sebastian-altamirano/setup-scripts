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

/** @param {string} fileName */
function getPythonTestFileName(fileName) {
	return fileName.endsWith("_test.py") ? fileName : `${fileName.slice(0, -3)}_test.py`;
}

/**
 * @type {import('lint-staged').Config}
 */
export default {
	"*.{json,md}": "prettier --write",
	"*.{mjs,js}": ["prettier --write", "eslint"],
	"*.psd1": (fileNames) => fileNames.map(formatPowerShellScript),
	"*.{ps1,psm1}": (fileNames) =>
		fileNames
			.map((fileName) => [formatPowerShellScript(fileName), lintPowerShellScript(fileName)])
			.flat(),
	"*.py": (fileNames) => {
		/** @type {Set<string>} */
		const testFileNames = new Set([]);

		return fileNames
			.map((fileName) => {
				const operations = [
					`pdm run -p src/ubuntu isort ${fileName}`,
					`pdm run -p src/ubuntu black ${fileName}`,
					`pdm run -p src/ubuntu mypy ${fileName}`,
					`pdm run -p src/ubuntu pylint ${fileName}`,
				];

				const testFileName = getPythonTestFileName(fileName);
				// Run the test only if it has not yet run.
				if (!testFileNames.has(testFileName)) {
					testFileNames.add(testFileName);
					operations.push(`pdm run -p src/ubuntu unittest ${testFileName}`);
				}

				return operations;
			})
			.flat();
	},
	"config/settings?(.schema).json": "scripts/validate-settings.ps1",
	"src/ubuntu/pyproject.toml": "npm run update-linux-requirements",
};
