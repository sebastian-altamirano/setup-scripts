import js from "@eslint/js";
import markdown from "@eslint/markdown";
import prettier from "eslint-config-prettier/flat";
import { defineConfig } from "eslint/config";
import globals from "globals";
import ts, { parser as tsParser } from "typescript-eslint";

export default defineConfig([
	{
		extends: ["markdown/recommended"],
		files: ["**/*.md"],
		language: "markdown/gfm",
		plugins: { markdown },
		rules: {
			"markdown/no-duplicate-headings": "error",
			"markdown/no-html": "error",
		},
	},
	{
		extends: ["js/recommended", "ts/strictTypeChecked", "ts/stylisticTypeChecked"],
		files: ["**/*.{js,mjs,ts}"],
		languageOptions: {
			ecmaVersion: 2022,
			globals: globals.browser,
			parser: tsParser,
			parserOptions: {
				projectService: true,
				tsconfigRootDir: import.meta.dirname,
			},
			sourceType: "module",
		},
		plugins: { js, ts },
		rules: {
			"@typescript-eslint/explicit-function-return-type": "off",
			complexity: ["error", 10],
			eqeqeq: "error",
			"no-console": "error",
			"no-lonely-if": "error",
			"no-var": "error",
			"no-warning-comments": "warn",
			yoda: "error",
		},
	},
	{
		files: ["**/*.ts"],
		rules: {
			"@typescript-eslint/explicit-function-return-type": "error",
		},
	},
	prettier,
]);
