"""Contains tests for the functions defined in `installation_steps.py`."""

# pylint: disable=missing-function-docstring

from ast import AST, Call, FunctionDef, Import, ImportFrom
from ast import Name as AstName
from ast import NodeVisitor
from ast import parse as parseAst
from inspect import getsource as getSource
from inspect import unwrap
from logging import ERROR as LOGGING_LEVEL_ERROR
from logging import INFO as LOGGING_LEVEL_INFO
from logging import LogRecord
from typing import Any, List, Optional, Tuple
from unittest import TestCase
from unittest.mock import ANY, Mock, call, patch

import dotfiles.installation_steps as installationSteps
from dotfiles.helpers.utils import installationStep
from dotfiles.installation_steps import (
    configureGit,
    copyApplicationSettings,
    installVSCodeExtensions,
)
from dotfiles.type_definitions import (
    ApplicationSettingsMapping,
    BasicGitConfiguration,
    GitConfiguration,
    GitConfigurationWithGpgCommitSigning,
)


@patch("dotfiles.installation_steps.formatConfigurationBlocks")
@patch("dotfiles.installation_steps.createOrUpdateFile")
@patch("dotfiles.installation_steps.getAbsolutePath")
@patch("dotfiles.installation_steps.runWithSh")
@patch("dotfiles.installation_steps.copyConfiguration")
class ConfigureGitTests(TestCase):
    """Contains tests for the `configureGit` function."""

    def setUp(self) -> None:
        self.gpgKeyId = "BIH6SLDZCKZ7L8TG2BCTY4HDIT0MOZUQQNTZ8HOF"
        self.gpgKeyInformation = (
            "sec   rsa4096 2024-01-01 [SC]\n"
            f"{self.gpgKeyId}\n"
            "uid                      John Doe <john.doe@example.com>\n"
            "ssb   rsa4096 2024-01-01 [E]\n"
        )
        self.gitConfigurationWithoutCommitSigning: BasicGitConfiguration = {
            "userName": "John Doe",
            "email": "john.doe@example.com",
        }
        self.gitConfigurationWithGpgCommitSigning: GitConfigurationWithGpgCommitSigning = {
            **self.gitConfigurationWithoutCommitSigning,
            "gpg": {
                "privateKeyName": "github.gpg",
            },
            "signingMethod": "gpg",
        }

    def testIfKeyIdIsParsedCorrectly(
        self,
        _mockCopyConfiguration: Mock,
        mockRunWithSh: Mock,
        _mockGetAbsolutePath: Mock,
        _mockCreateOrUpdateFile: Mock,
        _mockFormatConfigurationBlocks: Mock,
    ) -> None:
        mockRunWithSh.return_value.stdout = self.gpgKeyInformation

        configureGit(self.gitConfigurationWithGpgCommitSigning)

        mockRunWithSh.assert_any_call("git", "config", "--global", "user.signingkey", self.gpgKeyId)

    def testIfKeyTrustLevelIsChangedToUltimate(
        self,
        _mockCopyConfiguration: Mock,
        mockRunWithSh: Mock,
        _mockGetAbsolutePath: Mock,
        _mockCreateOrUpdateFile: Mock,
        _mockFormatConfigurationBlocks: Mock,
    ) -> None:
        mockRunWithSh.return_value.stdout = self.gpgKeyInformation

        configureGit(self.gitConfigurationWithGpgCommitSigning)

        mockRunWithSh.assert_any_call(
            "gpg", "--import-ownertrust", pipedInput=f"{self.gpgKeyId}:6:\n"
        )

    def testIfGpgAgentConfigurationIsCreated(
        self,
        _mockCopyConfiguration: Mock,
        mockRunWithSh: Mock,
        _mockGetAbsolutePath: Mock,
        mockCreateOrUpdateFile: Mock,
        mockFormatConfigurationBlocks: Mock,
    ) -> None:
        gitConfiguration: GitConfiguration = {
            **self.gitConfigurationWithoutCommitSigning,
            "commitSigning": {
                "allowCommittingFromVSCode": True,
                "cachePassPhraseDuringSession": True,
            },
            "gpg": {
                "privateKeyName": "github.gpg",
            },
            "signingMethod": "gpg",
        }
        mocksManager = Mock()
        mocksManager.attach_mock(mockCreateOrUpdateFile, "mockCreateOrUpdateFile")
        mocksManager.attach_mock(mockRunWithSh, "mockRunWithSh")

        configureGit(gitConfiguration)

        mockFormatConfigurationBlocks.assert_called_once()
        mocksManager.assert_has_calls(
            [
                call.mockCreateOrUpdateFile(
                    "~/.gnupg/gpg-agent.conf", mockFormatConfigurationBlocks.return_value
                ),
                call.mockRunWithSh("gpg-connect-agent", "reloadagent", "/bye"),
            ]
        )

    def testIfGpgAgentConfigurationIsNotCreated(
        self,
        _mockCopyConfiguration: Mock,
        mockRunWithSh: Mock,
        _mockGetAbsolutePath: Mock,
        mockCreateOrUpdateFile: Mock,
        mockFormatConfigurationBlocks: Mock,
    ) -> None:
        mocksManager = Mock()
        mocksManager.attach_mock(mockCreateOrUpdateFile, "mockRunWithSh")
        mocksManager.attach_mock(mockRunWithSh, "mockRunWithSh")

        configureGit(self.gitConfigurationWithGpgCommitSigning)

        mockFormatConfigurationBlocks.assert_not_called()
        self.assertTrue(
            call("~/.gnupg/gpg-agent.conf", mockFormatConfigurationBlocks.return_value)
            not in mockCreateOrUpdateFile.mock_calls
        )
        self.assertTrue(
            call(
                "gpg-connect-agent",
                "reloadagent",
                "/bye",
                mockFormatConfigurationBlocks.return_value,
            )
            not in mockRunWithSh.mock_calls
        )


@patch("dotfiles.installation_steps.runWithSh")
@patch("dotfiles.installation_steps.copyConfiguration")
class CopyApplicationSettingsTests(TestCase):
    """Contains tests for the `copyApplicationSettings` function."""

    def testIfResourceIsCopied(
        self,
        mockCopyConfiguration: Mock,
        _mockRunWithSh: Mock,
    ) -> None:
        settingsMapping: ApplicationSettingsMapping = {
            "resourceName": "fish",
            "destination": "~/.config/fish",
        }

        copyApplicationSettings([settingsMapping])

        mockCopyConfiguration.assert_called_once_with(
            settingsMapping["resourceName"], settingsMapping["destination"]
        )

    def testIfAllResourcesAreCopied(
        self,
        mockCopyConfiguration: Mock,
        _mockRunWithSh: Mock,
    ) -> None:
        settingsMappings: List[ApplicationSettingsMapping] = [
            {
                "resourceName": "fish",
                "destination": "~/.config/fish",
            },
            {"resourceName": ".gitconfig", "destination": "~/.gitconfig"},
        ]

        copyApplicationSettings(settingsMappings)

        self.assertEqual(len(settingsMappings), mockCopyConfiguration.call_count)

    def testIfCompletionCommandsAreExecutedAfterTheResourceIsCopied(
        self,
        mockCopyConfiguration: Mock,
        mockRunWithSh: Mock,
    ) -> None:
        mocksManager = Mock()
        mocksManager.attach_mock(mockCopyConfiguration, "mockCopyConfiguration")
        mocksManager.attach_mock(mockRunWithSh, "mockRunWithSh")
        settingMapping: ApplicationSettingsMapping = {
            "resourceName": "fish",
            "destination": "~/.config/fish",
            "completionCommands": [["echo", "Hello"], ["echo", "Bye"]],
        }
        anotherSettingsMapping: ApplicationSettingsMapping = {
            "resourceName": ".gitconfig",
            "destination": "~/.gitconfig",
            "completionCommands": [["echo", "Hello again"]],
        }
        settingsMappings: List[ApplicationSettingsMapping] = [
            settingMapping,
            anotherSettingsMapping,
        ]

        with self.assertLogs(level=LOGGING_LEVEL_INFO) as loggerSpy:
            copyApplicationSettings(settingsMappings)

        self.assertEqual(
            [
                call.mockCopyConfiguration(ANY, settingMapping["destination"]),
                call.mockRunWithSh(*settingMapping["completionCommands"][0]),
                call.mockRunWithSh(*settingMapping["completionCommands"][1]),
                call.mockCopyConfiguration(ANY, anotherSettingsMapping["destination"]),
                call.mockRunWithSh(*anotherSettingsMapping["completionCommands"][0]),
            ],
            mocksManager.mock_calls,
        )
        self.assertEqual(
            len([mapping for mapping in settingsMappings if "completionCommands" in mapping]),
            len(
                [
                    record.getMessage()
                    for record in loggerSpy.records
                    if record.getMessage() == "Running completion commands..."
                ]
            ),
        )

    def testIfPostInstallationInstructionsAreReturned(self, *_args: Tuple[Mock, Mock]) -> None:
        settingMapping: ApplicationSettingsMapping = {
            "resourceName": "fish",
            "destination": "~/.config/fish",
            "postInstallationInstructions": (
                "This is where I would put my post-installation instructions, if I had any!"
            ),
        }
        anotherSettingsMapping: ApplicationSettingsMapping = {
            "resourceName": ".gitconfig",
            "destination": "~/.gitconfig",
            "postInstallationInstructions": "There is nothing else to do...",
        }
        settingMappings = [settingMapping, anotherSettingsMapping]
        expectedPostInstallationInstructions: List[str] = [
            settingMapping["postInstallationInstructions"],
            anotherSettingsMapping["postInstallationInstructions"],
        ]

        postInstallationInstructions = copyApplicationSettings(settingMappings)

        self.assertEqual(expectedPostInstallationInstructions, postInstallationInstructions)

    def testIfCompletionCommandsAndPostInstallationInstructionsAreOptional(
        self,
        _mockCopyConfiguration: Mock,
        mockRunWithSh: Mock,
    ) -> None:
        settingsMapping: List[ApplicationSettingsMapping] = [
            {
                "resourceName": "fish",
                "destination": "~/.config/fish",
            }
        ]

        postInstallationInstructions = copyApplicationSettings(settingsMapping)

        mockRunWithSh.assert_not_called()
        self.assertEqual([], postInstallationInstructions)

    def testIfTheResourcesAreLoggedAsTheyAreCopied(self, *_args: Tuple[Mock, Mock]) -> None:
        settingsMappings: List[ApplicationSettingsMapping] = [
            {
                "resourceName": "fish",
                "destination": "~/.config/fish",
            },
            {"resourceName": ".gitconfig", "destination": "~/.gitconfig"},
        ]

        with self.assertLogs(level=LOGGING_LEVEL_INFO) as loggerSpy:
            unwrap(copyApplicationSettings)(settingsMappings)

        self.assertEqual(2, len(loggerSpy.records))
        self._assertResourceCopyLog(loggerSpy.records[0], settingsMappings[0])
        self._assertResourceCopyLog(loggerSpy.records[1], settingsMappings[1])

    def _assertResourceCopyLog(
        self, logRecord: LogRecord, settingsMapping: ApplicationSettingsMapping
    ) -> None:
        self.assertEqual(
            f'Copying "{settingsMapping["resourceName"]}" to "{settingsMapping["destination"]}"...',
            logRecord.getMessage(),
        )


@patch("dotfiles.installation_steps.runWithoutLogging")
class InstallVSCodeExtensionsTests(TestCase):
    """Contains tests for the `installVSCodeExtensions` function."""

    def testIfAllExtensionsAreInstalled(self, mockRunWithoutLogging: Mock) -> None:
        mockRunWithoutLogging.return_value.stderr = ""
        extensions = ["theme", "linter", "another-linter", "language-support"]

        with self.assertLogs(level=LOGGING_LEVEL_INFO) as loggerSpy:
            unwrap(installVSCodeExtensions)(extensions)

        mockRunWithoutLogging.assert_has_calls(
            [
                call(["code", "--install-extension", extension], capture_output=True, check=True)
                for extension in extensions
            ],
            any_order=True,
        )
        self.assertEqual(1, len(loggerSpy.records))
        self.assertEqual(
            "All extensions have been installed successfully.",
            loggerSpy.records[0].getMessage(),
        )

    def testIfExtensionsThatCouldNotBeInstalledAreLogged(self, mockRunWithoutLogging: Mock) -> None:
        extensionThatExists = "extension-that-exists"
        extensionThatDoesNotExist = "extension-that-does-not-exist"
        extensions = [extensionThatExists, extensionThatDoesNotExist]

        def fillStdErrIfExtensionDoesNotExist(arguments: List[str], **_kwargs: Any) -> Mock:
            return Mock(
                stderr="An error has occurred..."
                if arguments[2] == extensionThatDoesNotExist
                else ""
            )

        mockRunWithoutLogging.side_effect = fillStdErrIfExtensionDoesNotExist

        with self.assertLogs() as loggerSpy:
            unwrap(installVSCodeExtensions)(extensions)

        self.assertEqual(1, len(loggerSpy.records))
        self.assertEqual(LOGGING_LEVEL_ERROR, loggerSpy.records[0].levelno)
        self.assertEqual(
            f"Could not install the following extensions:\n- {extensionThatDoesNotExist}\n",
            loggerSpy.records[0].getMessage(),
        )


class GeneralTests(TestCase):
    """Contains tests that apply to all installation steps."""

    def testIfAllInstallationStepsAreDecorated(self) -> None:
        def assertInstallationStepIsDecorated(node: FunctionDef) -> None:
            installationStepName = node.name
            decorators = node.decorator_list
            self.assertTrue(
                any(
                    installationStep.__name__ == decorator.id
                    for decorator in decorators
                    if isinstance(decorator, AstName)
                ),
                f"`{installationStepName}` is not decorated with `{installationStep.__name__}`.",
            )

        class InstallationStepVisitor(NodeVisitor):
            """Node visitor to check that all installation steps are decorated."""

            def visit(self, node: AST) -> None:
                if isinstance(node, FunctionDef):
                    assertInstallationStepIsDecorated(node)
                self.generic_visit(node)

        abstractSintaxTree = parseAst(getSource(installationSteps))
        visitor = InstallationStepVisitor()
        visitor.visit(abstractSintaxTree)

    def testIfAllInstallationStepsUseRunWithInsteadOfRun(self) -> None:
        def assertInstalationStepUsesRunWith(functionName: str, installationStepName: str) -> None:
            self.assertNotEqual(
                functionName,
                # We are assuming that `subprocess.run` is imported as `from subprocess import run`.
                "run",
                f"`{installationStepName}` makes use of `subprocess.run`, replace it with "
                "`runWithSh`",
            )

        class InstallationStepVisitor(NodeVisitor):
            """
            Node visitor to check that all installation steps use `runWith...` instead of
            `subprocess.run`, but allowing the latter when called within the arguments of the
            former.
            """

            def __init__(self) -> None:
                self.installationStepName: Optional[str] = None
                self.isSubprocessImportedAsModule = False
                self.isSubprocessRunRenamed = False

            def _assertSubprocessRunIsImportedAsExpected(self) -> None:
                # This is done to simplify the test.
                assert (
                    not self.isSubprocessImportedAsModule and not self.isSubprocessRunRenamed
                ), "`subprocess.run` must be imported as `from subprocess import run`"

            def visit(self, node: AST) -> Any:
                super().visit(node)
                self._assertSubprocessRunIsImportedAsExpected()

            def visit_Call(self, node: Call) -> None:  # pylint: disable=invalid-name
                if self.installationStepName and (functionName := getattr(node.func, "id", None)):
                    assertInstalationStepUsesRunWith(functionName, self.installationStepName)
                # It is OK to call `run` within the arguments of `runWith...`, that is why
                # `generic_visit` is not called.

            def visit_FunctionDef(self, node: FunctionDef) -> None:  # pylint: disable=invalid-name
                self.installationStepName = node.name
                self.generic_visit(node)
                self.installationStepName = None

            def visit_ImportFrom(self, node: ImportFrom) -> None:  # pylint: disable=invalid-name
                if node.module == "subprocess" and any(
                    importName.name == "run" and importName.asname is not None
                    for importName in node.names
                ):
                    self.isSubprocessRunRenamed = True
                else:
                    self.generic_visit(node)

            def visit_Import(self, node: Import) -> None:  # pylint: disable=invalid-name
                if any(importName.name == "subprocess" for importName in node.names):
                    self.isSubprocessImportedAsModule = True
                else:
                    self.generic_visit(node)

        abstractSintaxTree = parseAst(getSource(installationSteps))
        visitor = InstallationStepVisitor()
        visitor.visit(abstractSintaxTree)
