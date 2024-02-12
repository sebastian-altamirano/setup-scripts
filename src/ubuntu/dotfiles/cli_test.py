"""Contains tests for the functions defined in `cli.py`."""

# pylint: disable=missing-function-docstring

from datetime import datetime
from logging import ERROR as LOGGING_LEVEL_ERROR
from os.path import join as joinPaths
from pathlib import Path
from unittest import TestCase
from unittest.mock import ANY, Mock, call, patch

from dotfiles import __version__
from dotfiles.cli import main


@patch("dotfiles.cli.install")
@patch("dotfiles.cli.readAndValidateConfig")
@patch("dotfiles.cli.logWarnings")
@patch("dotfiles.cli.StreamHandler")
@patch("dotfiles.cli.getAbsolutePath")
@patch("dotfiles.cli.FileHandler")
@patch("dotfiles.cli.configureLogging")
@patch(
    "dotfiles.cli.ArgumentParser",
    return_value=Mock(parse_args=Mock(return_value=Mock(logFilePath="dotfiles-install.log"))),
)
class EntryPointTests(TestCase):
    """Contains tests for the application entry point."""

    def testIfInstallIsCalledWithAValidConfiguration(
        self,
        _mockArgumentParser: Mock,
        _mockConfigureLogging: Mock,
        _mockFileHandler: Mock,
        _mockGetAbsolutePath: Mock,
        _mockStreamHandler: Mock,
        _mockLogWarnings: Mock,
        mockReadAndValidateConfig: Mock,
        mockInstall: Mock,
    ) -> None:
        main()

        mockInstall.assert_called_once_with(mockReadAndValidateConfig.return_value)

    @patch("dotfiles.cli.datetime")
    def testIfArgumentParserIsConfigured(
        self,
        mockDateTime: Mock,
        mockArgumentParser: Mock,
        _mockConfigureLogging: Mock,
        _mockFileHandler: Mock,
        _mockGetAbsolutePath: Mock,
        _mockStreamHandler: Mock,
        _mockLogWarnings: Mock,
        _mockReadAndValidateConfig: Mock,
        _mockInstall: Mock,
    ) -> None:
        now = datetime.now()
        mockDateTime.now = Mock(datetime, return_value=now)
        arguments = ["install.py", "--logFilePath", "dotfiles-install.log"]

        with patch("dotfiles.cli.argv", arguments):
            main()

        mockArgumentParser.return_value.add_argument.assert_has_calls(
            [
                call(
                    "--logFilePath",
                    default=(
                        joinPaths(
                            Path.home(),
                            f"dotfiles_install-{now.strftime('%Y_%m_%d-%H_%M_%S')}.log",
                        )
                    ),
                    help=ANY,
                    type=str,
                ),
                call("--version", action="version", version=__version__),
            ]
        )
        mockArgumentParser.return_value.parse_args.assert_called_once_with(arguments[1:])

    def testIfLoggerIsConfigured(  # pylint: disable=too-many-arguments
        self,
        _mockArgumentParser: Mock,
        mockConfigureLogging: Mock,
        mockFileHandler: Mock,
        mockGetAbsolutePath: Mock,
        mockStreamHandler: Mock,
        mockLogWarnings: Mock,
        _mockReadAndValidateConfig: Mock,
        _mockInstall: Mock,
    ) -> None:
        logFilePath = "dotfiles-install.log"
        arguments = ["install.py", "--logFilePath", logFilePath]

        with patch("dotfiles.cli.argv", arguments):
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
        _mockArgumentParser: Mock,
        _mockConfigureLogging: Mock,
        _mockFileHandler: Mock,
        _mockGetAbsolutePath: Mock,
        _mockStreamHandler: Mock,
        _mockLogWarnings: Mock,
        _mockReadAndValidateConfig: Mock,
        mockInstall: Mock,
    ) -> None:
        mockInstall.side_effect = Exception

        with self.assertLogs() as loggerSpy, self.assertRaises(Exception):
            main()

        self.assertEqual(1, len(loggerSpy.records))
        logRecord = loggerSpy.records[0]
        self.assertEqual("Installation failed.", logRecord.getMessage())
        self.assertEqual(LOGGING_LEVEL_ERROR, logRecord.levelno)
