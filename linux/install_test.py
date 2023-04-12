# pylint: disable=C0116

"""Contains tests for the functions defined in `install.py`."""

from logging import ERROR as LOGGING_LEVEL_ERROR
from pathlib import Path
from typing import cast
from unittest import TestCase
from unittest.mock import ANY, Mock, call, patch

from linux.install import UNSUPPORTED_CONFIGURATION_KEYS, install, main
from linux.type_definitions import Config


@patch("linux.install.install")
@patch(
    "linux.install.ArgumentParser",
    return_value=Mock(parse_args=Mock(return_value=Mock(logFilePath="dotfiles-install.log"))),
)
@patch("linux.install.configureLogging")
@patch("linux.install.FileHandler")
class EntrypointTests(TestCase):
    """Contains tests for the entrypoint of the file."""

    def testIfInstallIsCalled(
        self,
        _mockFileHandler: Mock,
        _mockConfigureLogging: Mock,
        _mockArgumentParser: Mock,
        mockInstall: Mock,
    ) -> None:
        main()

        mockInstall.assert_called_once()

    def testIfArgumentParserIsConfigured(
        self,
        _mockFileHandler: Mock,
        _mockConfigureLogging: Mock,
        mockArgumentParser: Mock,
        _mockInstall: Mock,
    ) -> None:
        arguments = ["install.py", "--logFilePath", "dotfiles-install.log"]

        with patch("linux.install.argv", arguments):
            main()

        mockArgumentParser.return_value.add_argument.assert_has_calls(
            [
                call(
                    "--logFilePath",
                    default=f"{Path.home()}/dotfiles-install.log",
                    help=ANY,
                    type=str,
                ),
                call("--version", action="version", version=ANY),
            ]
        )
        mockArgumentParser.return_value.parse_args.assert_called_once_with(arguments[1:])

    @patch("linux.install.getAbsolutePath")
    @patch("linux.install.logWarnings")
    @patch("linux.install.StreamHandler")
    def testIfLoggerIsConfigured(
        self,
        mockStreamHandler: Mock,
        mockLogWarnings: Mock,
        mockGetAbsolutePath: Mock,
        mockFileHandler: Mock,
        mockConfigureLogging: Mock,
        _mockArgumentParser: Mock,
        _mockInstall: Mock,
    ) -> None:
        logFilePath = "dotfiles-install.log"
        arguments = ["install.py", "--logFilePath", logFilePath]

        with patch("linux.install.argv", arguments):
            main()

        # Logger must be configured to log to the console and to a file
        mockConfigureLogging.assert_called_once_with(
            level=ANY,
            format=ANY,
            handlers=[
                mockFileHandler.return_value,
                mockStreamHandler.return_value,
            ],
        )
        # Logger must be configured to log to a file located at `--logFilePath`.
        mockFileHandler.assert_called_once_with(mockGetAbsolutePath.return_value)
        # `--logFilePath` can be relative.
        mockGetAbsolutePath.assert_called_once_with(logFilePath)
        mockLogWarnings.assert_called_once()

    def testIfExceptionsThatOccurInInstallAreLogged(
        self,
        _mockFileHandler: Mock,
        _mockConfigureLogging: Mock,
        _mockArgumentParser: Mock,
        mockInstall: Mock,
    ) -> None:
        mockInstall.side_effect = Exception

        with self.assertLogs() as loggerSpy, self.assertRaises(Exception):
            main()

        self.assertEqual(1, len(loggerSpy.records))
        logRecord = loggerSpy.records[0]
        self.assertEqual("Installation failed.", logRecord.getMessage())
        self.assertEqual(LOGGING_LEVEL_ERROR, logRecord.levelno)


@patch("linux.install.installFish")
@patch("linux.install.upgradeSystemDependencies")
@patch("linux.install.installPackages")
@patch("linux.install.installVSCodeExtensions")
@patch("linux.install.copyApplicationSettings")
@patch("linux.install.warnAboutUnsupportedConfig")
@patch("linux.install.logCompletionMessage")
@patch("linux.install.readJson")
class InstallTests(TestCase):
    """Contains tests for the `install` function."""

    def testIfAllConfigurationKeysAreOptional(
        self,
        mockReadJson: Mock,
        mockLogCompletionMessage: Mock,
        mockWarnAboutUnsupportedConfig: Mock,
        mockCopyApplicationSettings: Mock,
        mockInstallVSCodeExtensions: Mock,
        mockInstallPackages: Mock,
        mockUpgradeSystemDependencies: Mock,
        mockInstallFish: Mock,
    ) -> None:
        emptyConfiguration: Config = {}
        mockReadJson.return_value = emptyConfiguration

        install()

        mockInstallFish.assert_called()
        mockUpgradeSystemDependencies.assert_called()
        mockInstallPackages.assert_called()
        mockWarnAboutUnsupportedConfig.assert_not_called()
        mockInstallVSCodeExtensions.assert_not_called()
        mockCopyApplicationSettings.assert_not_called()
        mockLogCompletionMessage.assert_called()

    def testIfPostInstallationInstructionAreCollectedAndDisplayed(
        self,
        mockReadJson: Mock,
        mockLogCompletionMessage: Mock,
        _mockWarnAboutUnsupportedConfig: Mock,
        mockCopyApplicationSettings: Mock,
        _mockInstallVSCodeExtensions: Mock,
        mockInstallPackages: Mock,
        _mockUpgradeSystemDependencies: Mock,
        _mockInstallFish: Mock,
    ) -> None:
        configuration: Config = {
            "settingsPaths": [
                {
                    "resourceName": "fish",
                    "destination": "~/.config/fish",
                    "completionCommands": [["echo", "Hello"], ["echo", "Bye"]],
                }
            ]
        }
        mockReadJson.return_value = configuration
        mockInstallPackages.return_value = ["Post installation instructions..."]
        mockCopyApplicationSettings.return_value = ["More post installation instructions..."]
        expectedPostInstallationInstructions = [
            *mockInstallPackages.return_value,
            *mockCopyApplicationSettings.return_value,
        ]

        install()

        mockLogCompletionMessage.assert_called_once_with(expectedPostInstallationInstructions)

    def testIfWarningsAreProducedForUnsupportedKeys(
        self,
        mockReadJson: Mock,
        _mockLogCompletionMessage: Mock,
        mockWarnAboutUnsupportedConfig: Mock,
        _mockCopyApplicationSettings: Mock,
        _mockInstallVSCodeExtensions: Mock,
        _mockInstallPackages: Mock,
        _mockUpgradeSystemDependencies: Mock,
        _mockInstallFish: Mock,
    ) -> None:
        unsupportedConfiguration: Config = cast(
            Config, {key: "Unsupported configuration" for key in UNSUPPORTED_CONFIGURATION_KEYS}
        )
        mockReadJson.return_value = unsupportedConfiguration

        install()

        mockWarnAboutUnsupportedConfig.assert_has_calls(
            [call(key) for key in unsupportedConfiguration]
        )
