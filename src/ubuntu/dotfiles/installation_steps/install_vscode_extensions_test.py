"""Contains tests for the installation step defined in `install_vscode_extensions.py`."""

# pylint: disable=missing-function-docstring

from inspect import unwrap
from logging import ERROR as LOGGING_LEVEL_ERROR
from logging import INFO as LOGGING_LEVEL_INFO
from unittest import TestCase
from unittest.mock import Mock, call, patch

from dotfiles.installation_steps.install_vscode_extensions import installVSCodeExtensions


@patch("dotfiles.installation_steps.install_vscode_extensions.runWithSh")
class InstallVSCodeExtensionsTests(TestCase):
    """Contains tests for the `installVSCodeExtensions` function."""

    def testIfAllExtensionsAreInstalled(self, mockRunWithSh: Mock) -> None:
        mockRunWithSh.return_value.stderr = ""
        extensions = ["theme", "linter", "another-linter", "language-support"]

        with self.assertLogs(level=LOGGING_LEVEL_INFO) as loggerSpy:
            unwrap(installVSCodeExtensions)(extensions)

        mockRunWithSh.assert_has_calls(
            [call("code", "--install-extension", extension) for extension in extensions],
            any_order=True,
        )
        self.assertEqual(1, len(loggerSpy.records))
        self.assertEqual(
            "All extensions have been installed successfully.",
            loggerSpy.records[0].getMessage(),
        )

    def testIfExtensionsThatCouldNotBeInstalledAreLogged(self, mockRunWithSh: Mock) -> None:
        extensionThatExists = "extension-that-exists"
        extensionThatDoesNotExist = "extension-that-does-not-exist"
        extensions = [extensionThatExists, extensionThatDoesNotExist]

        def fillStdErrIfExtensionDoesNotExist(*args: str) -> Mock:
            return Mock(
                stderr="An error has occurred..." if args[2] == extensionThatDoesNotExist else ""
            )

        mockRunWithSh.side_effect = fillStdErrIfExtensionDoesNotExist

        with self.assertLogs() as loggerSpy:
            unwrap(installVSCodeExtensions)(extensions)

        self.assertEqual(1, len(loggerSpy.records))
        self.assertEqual(LOGGING_LEVEL_ERROR, loggerSpy.records[0].levelno)
        self.assertEqual(
            f"Could not install the following extensions:\n- {extensionThatDoesNotExist}\n",
            loggerSpy.records[0].getMessage(),
        )
