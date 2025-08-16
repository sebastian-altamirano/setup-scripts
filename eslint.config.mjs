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
		// @ts-expect-error `@eslint/markdown` does not support `exactOptionalPropertyTypes`.
		plugins: { markdown },
		rules: {
			"markdown/no-duplicate-headings": "error",
			"markdown/no-html": "error",
		},
	},
	{
		extends: ["js/recommended", "ts/strictTypeChecked", "ts/stylisticTypeChecked"],
		files: ["**/*.{js,mjs}"],
		languageOptions: {
			ecmaVersion: 2022,
			globals: globals.browser,
			// @ts-expect-error `typescript-eslint` uses the type definitions provided by TSESLint, which
			// are not compatible with native ESLint types.
			parser: tsParser,
			parserOptions: {
				projectService: true,
				tsconfigRootDir: import.meta.dirname,
			},
			sourceType: "module",
		},
		// @ts-expect-error `typescript-eslint` uses the type definitions provided by TSESLint, which
		// are not compatible with native ESLint types.
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
	prettier,
]);
