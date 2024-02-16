/// <reference types="lint-staged" />

import { existsSync } from "node:fs";
import { dirname } from "node:path";
import { fileURLToPath } from "node:url";

/**
 * @param {string} fileName
 *
 * @return {string}
 */
function formatPowerShellScript(fileName) {
	return `scripts/format-powershell.ps1 \
-Path ${fileName} \
-SettingsPath src/windows/formatter-settings.psd1`;
}

/**
 * @param {string} fileName
 *
 * @return {string}
 */
function lintPowerShellScript(fileName) {
	return `scripts/lint-powershell.ps1 \
-Path ${fileName} \
-SettingsPath src/windows/linter-settings.psd1`;
}

/**
 * @param {string} fileName
 *
 * @example
 * getPythonTestFileName("foo_test.py") // "foo_test.py"
 * @example
 * getPythonTestFileName("foo.py") // "foo_test.py" (if it exists)
 * @example
 * getPythonTestFileName("foo.py") // null (if `foo_test.py` doesn't exist)
 *
 * @returns {string | null}
 */
function getPythonTestFileName(fileName) {
	if (fileName.endsWith("_test.py")) {
		return fileName;
	}

	const testFileName = `${fileName.slice(0, -3)}_test.py`;
	return existsSync(testFileName) ? testFileName : null;
}

/**
 * @type {import('lint-staged').Config}
 */
export default {
	"*.{json,md}": "prettier --write",
	"*.{mjs,js}": ["prettier --write", "eslint"],
	"*.psd1": (fileNames) => fileNames.map(formatPowerShellScript),
	"*.{ps1,psm1}": (fileNames) =>
		fileNames.flatMap((fileName) => [
			formatPowerShellScript(fileName),
			lintPowerShellScript(fileName),
		]),
	"*.py": (fileNames) => {
		/** @type {Set<string>} */
		const testFileNames = new Set([]);

		const operations = fileNames.flatMap((fileName) => {
			const fileOperations = [
				`pdm run -p src/ubuntu isort ${fileName}`,
				`pdm run -p src/ubuntu black ${fileName}`,
				`pdm run -p src/ubuntu mypy ${fileName}`,
				`pdm run -p src/ubuntu pylint ${fileName}`,
			];

			const testFileName = getPythonTestFileName(fileName);
			// Run the test only if it has not yet run.
			if (testFileName && !testFileNames.has(testFileName)) {
				testFileNames.add(testFileName);
				fileOperations.push(`pdm run -p src/ubuntu unittest ${testFileName}`);
			}

			return fileOperations;
		});
		// Always run static analysis tests.
		operations.push(
			`pdm run -p src/ubuntu unittest ${dirname(
				fileURLToPath(import.meta.url),
			)}/src/ubuntu/dotfiles/tests/static_analysis_test.py`,
		);

		return operations;
	},
	"config/settings?(.schema).json": "scripts/validate-settings.ps1",
	"src/ubuntu/pyproject.toml": "npm run update-linux-requirements",
};
