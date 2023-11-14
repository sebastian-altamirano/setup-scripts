/// <reference types="eslint" />

import js from "@eslint/js";
import globals from "globals";

/**
 * @type {import('eslint').Linter.FlatConfig[]}
 */
export default [
	{
		...js.configs.recommended,
		files: ["src/browser-snippets/**/*.mjs"],
		languageOptions: {
			ecmaVersion: "latest",
			globals: { ...globals.browser, ...globals.es2021 },
			sourceType: "module",
		},
	},
];
