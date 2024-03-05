/// <reference types="lint-staged" />

import { existsSync } from "node:fs";

/**
 * @param {string} filePath
 *
 * @return {string}
 */
function formatPowerShellScript(filePath) {
	return `scripts/format-powershell.ps1 \
-Path ${filePath} \
-SettingsPath src/windows/formatter-settings.psd1`;
}

/**
 * @param {string} filePath
 *
 * @return {string}
 */
function lintPowerShellScript(filePath) {
	return `scripts/lint-powershell.ps1 \
-Path ${filePath} \
-SettingsPath src/windows/linter-settings.psd1`;
}

/**
 * @param {string} filePath
 *
 * @example
 * getPythonTestFilePath("foo_test.py") // "foo_test.py"
 * @example
 * getPythonTestFilePath("foo.py") // "foo_test.py" (if it exists)
 * @example
 * getPythonTestFilePath("foo.py") // null (if `foo_test.py` doesn't exist)
 *
 * @returns {string | null}
 */
function getPythonTestFilePath(filePath) {
	if (filePath.endsWith("_test.py")) {
		return filePath;
	}

	const testFilePath = `${filePath.slice(0, -3)}_test.py`;
	return existsSync(testFilePath) ? testFilePath : null;
}

/**
 * @param {string[]} filePaths
 *
 * @returns {string[]}
 */
function getPythonTestFilePaths(filePaths) {
	// Use a set to avoid running the same test more than once.
	/** @type {Set<string>} */
	const testFilePaths = new Set([
		// Always run static analysis tests.
		`${import.meta.dirname}/src/ubuntu/dotfiles/tests/static_analysis_test.py`,
	]);

	filePaths.forEach((filePath) => {
		const testFilePath = getPythonTestFilePath(filePath);
		if (testFilePath !== null) {
			testFilePaths.add(testFilePath);
		}
	});

	return [...testFilePaths];
}

/**
 * @type {import('lint-staged').Config}
 */
export default {
	"*.{json,md}": "prettier --write",
	"*.{mjs,js}": ["prettier --write", "eslint"],
	"*.psd1": (filePaths) => filePaths.map(formatPowerShellScript),
	"*.{ps1,psm1}": (filePaths) =>
		filePaths.flatMap((filePath) => [
			formatPowerShellScript(filePath),
			lintPowerShellScript(filePath),
		]),
	"*.py": (filePaths) => {
		const spaceSeparatedFilePaths = filePaths.join(" ");
		const commands = [
			`pdm run -p src/ubuntu isort ${spaceSeparatedFilePaths}`,
			`pdm run -p src/ubuntu black ${spaceSeparatedFilePaths}`,
			`pdm run -p src/ubuntu mypy ${spaceSeparatedFilePaths}`,
			`pdm run -p src/ubuntu pylint ${spaceSeparatedFilePaths}`,
		];

		const testFilePaths = getPythonTestFilePaths(filePaths);
		if (testFilePaths.length) {
			commands.push(`pdm run -p src/ubuntu unittest ${testFilePaths.join(" ")}`);
		}

		return commands;
	},
	"src/ubuntu/pyproject.toml": "npm run update-linux-requirements",
};
