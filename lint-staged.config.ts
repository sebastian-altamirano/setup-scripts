import type { Configuration } from "lint-staged";

function formatPathsForPowerShell(filePaths: readonly string[]): string {
	return filePaths.map((filePath) => `'${filePath}'`).join(",");
}

/**
 * Some tasks are intentionally repeated to avoid race conditions, as recommended in the lint-staged
 * documentation.
 */
const config: Configuration = {
	"*.bash": ["shfmt -w", "shellcheck"],
	"*.fish": "fish_indent -w",
	"*.{json,jsonc}": "prettier --write",
	"*.md": [
		"doctoc --github --minlevel 2 --title '## Table of Contents' --update-only",
		"prettier --write",
		"eslint --fix",
	],
	"*.{mjs,js,ts}": [(): string => "tsc", `prettier --write`, `eslint --fix`],
	"*.{ps1,psm1}": (filePaths) => [
		`pwsh -Command 'scripts/code-quality.ps1' -Action format -Type powershell -Path ${formatPathsForPowerShell(filePaths)}`,
		`pwsh -Command 'scripts/code-quality.ps1' -Action lint -Type powershell -Path ${formatPathsForPowerShell(filePaths)}`,
	],
	"*.psd1": (filePaths) =>
		`pwsh -Command 'scripts/code-quality.ps1' -Action lint -Type powershell -Path ${formatPathsForPowerShell(filePaths)}`,
};

export default config;
