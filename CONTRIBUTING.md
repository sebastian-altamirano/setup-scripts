# Contributing

## Requirements

- Fish shell 4+
- PowerShell 7.5+
- Node.js and PNPM (check the required versions in the `devEngines` key of [`package.json`](./package.json))
- PSScriptAnalyzer
- ShellCheck
- shfmt

Once all the requirements are installed, run `pnpm i` to install the development dependencies.

## Development checks

Linting and formatting are executed in a pre-commit hook using lint-staged. These checks can also be run for all files using the commands configured in the `scripts` section of [`package.json`](./package.json).
