/// <reference types="lint-staged" />

import { resolve } from "node:path";

/**
 * @type {import('lint-staged').Config}
 */
export default {
	"*.{json,md}": "prettier --write",
	"**/!(*.lintstagedrc.mjs)": () =>
		resolve(`${import.meta.dirname}/../scripts/validate-settings.ps1`),
};
