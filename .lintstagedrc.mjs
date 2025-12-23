/**
 * @param {readonly string[]} filePaths
 * @returns {string}
 */
function formatPathsForPowerShell(filePaths) {
	return filePaths.map((filePath) => `'${filePath}'`).join(",");
}

/**
 * Some tasks are intentionally repeated to avoid race conditions, as recommended in the lint-staged
 * documentation.
 *
 * @type {import('lint-staged').Configuration}
 */
export default {
	"*.bash": ["shfmt -w", "shellcheck"],
	"*.fish": "fish_indent -w",
	"*.{json,jsonc}": "prettier --write",
	"*.md": ["prettier --write", "eslint --fix"],
	"*.{mjs,js}": [() => "tsc", `prettier --write`, `eslint --fix`],
	"*.{ps1,psm1}": (filePaths) => [
		`pwsh -Command 'scripts/code-quality.ps1' -Action format -Type powershell -Path ${formatPathsForPowerShell(filePaths)}`,
		`pwsh -Command 'scripts/code-quality.ps1' -Action lint -Type powershell -Path ${formatPathsForPowerShell(filePaths)}`,
	],
	"*.psd1": (filePaths) =>
		`pwsh -Command 'scripts/code-quality.ps1' -Action lint -Type powershell -Path ${formatPathsForPowerShell(filePaths)}`,
};
