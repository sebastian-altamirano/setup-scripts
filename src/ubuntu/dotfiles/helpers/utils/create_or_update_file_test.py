"""Contains tests for the util defined in `create_or_update_file.py`."""

# pylint: disable=missing-function-docstring

from typing import Any, List, cast
from unittest import TestCase
from unittest.mock import Mock, call, patch

from dotfiles.helpers.utils.create_or_update_file import createOrUpdateFile


@patch("dotfiles.helpers.utils.create_or_update_file.createDirectories")
@patch("dotfiles.helpers.utils.create_or_update_file.open")
@patch("dotfiles.helpers.utils.create_or_update_file.pathExists")
@patch("dotfiles.helpers.utils.create_or_update_file.getAbsolutePath")
class CreateOrUpdateFileTests(TestCase):
    """Contains tests for the `createOrUpdateFile` function."""

    def setUp(self) -> None:
        self.filePath = "~/.config/fish/config.fish"
        self.fileContent = "set -gx GPG_TTY (tty)"

    def testIfFileIsCreated(
        self,
        mockGetAbsolutePath: Mock,
        mockPathExists: Mock,
        mockFileOpen: Mock,
        mockCreateDirectories: Mock,
    ) -> None:
        mockPathExists.return_value = False
        mocksManager = self._getMocksManager(
            mockGetAbsolutePath, mockPathExists, mockFileOpen, mockCreateDirectories
        )

        createOrUpdateFile(self.filePath, self.fileContent)

        self.assertEqual(
            [
                call.mockGetAbsolutePath(self.filePath),
                call.mockPathExists(mockGetAbsolutePath.return_value),
                call.mockCreateDirectories(mockGetAbsolutePath.return_value, exist_ok=True),
                call.mockFileWrite(self.fileContent),
                call.mockFileWrite("\n"),
            ],
            mocksManager.mock_calls,
        )
        mockFileOpen.assert_called_once_with(
            mockGetAbsolutePath.return_value, mode="w", encoding="utf-8"
        )

    def testIfEmptyFileIsUpdated(
        self,
        mockGetAbsolutePath: Mock,
        mockPathExists: Mock,
        mockFileOpen: Mock,
        mockCreateDirectories: Mock,
    ) -> None:
        mockFileRead = self._getMockFileRead(mockFileOpen)
        mockFileRead.return_value = ""
        expectedFileWriteCalls = [
            call.mockFileWrite(self.fileContent),
            call.mockFileWrite("\n"),
        ]

        self._assertFileIsUpdated(
            mockGetAbsolutePath,
            mockPathExists,
            mockFileOpen,
            mockCreateDirectories,
            expectedFileWriteCalls,
        )

    def testIfFileThatEndsWithNewlineIsUpdated(
        self,
        mockGetAbsolutePath: Mock,
        mockPathExists: Mock,
        mockFileOpen: Mock,
        mockCreateDirectories: Mock,
    ) -> None:
        mockFileRead = self._getMockFileRead(mockFileOpen)
        mockFileRead.return_value = "eval $(ssh-agent -c)\n"
        expectedFileWriteCalls = [
            call.mockFileWrite(self.fileContent),
            call.mockFileWrite("\n"),
        ]

        self._assertFileIsUpdated(
            mockGetAbsolutePath,
            mockPathExists,
            mockFileOpen,
            mockCreateDirectories,
            expectedFileWriteCalls,
        )

    def testIfFileThatDoesNotEndWithNewlineIsUpdated(
        self,
        mockGetAbsolutePath: Mock,
        mockPathExists: Mock,
        mockFileOpen: Mock,
        mockCreateDirectories: Mock,
    ) -> None:
        mockFileRead = self._getMockFileRead(mockFileOpen)
        mockFileRead.return_value = "eval $(ssh-agent -c)"
        expectedFileWriteCalls = [
            call.mockFileWrite("\n"),
            call.mockFileWrite(self.fileContent),
            call.mockFileWrite("\n"),
        ]

        self._assertFileIsUpdated(
            mockGetAbsolutePath,
            mockPathExists,
            mockFileOpen,
            mockCreateDirectories,
            expectedFileWriteCalls,
        )

    def testIfNewlineIsNotAddedWhenContentAlreadyEndsWithIt(
        self,
        mockGetAbsolutePath: Mock,
        mockPathExists: Mock,
        mockFileOpen: Mock,
        mockCreateDirectories: Mock,
    ) -> None:
        self.fileContent = "set -gx GPG_TTY (tty)\n"
        mockFileRead = self._getMockFileRead(mockFileOpen)
        mockFileRead.return_value = ""
        expectedFileWriteCalls = [call.mockFileWrite(self.fileContent)]

        self._assertFileIsUpdated(
            mockGetAbsolutePath,
            mockPathExists,
            mockFileOpen,
            mockCreateDirectories,
            expectedFileWriteCalls,
        )

    def _assertFileIsUpdated(  # pylint: disable=too-many-arguments
        self,
        mockGetAbsolutePath: Mock,
        mockPathExists: Mock,
        mockFileOpen: Mock,
        mockCreateDirectories: Mock,
        expectedFileWriteCalls: List[Any],
    ) -> None:
        mockPathExists.return_value = True
        mocksManager = self._getMocksManager(
            mockGetAbsolutePath, mockPathExists, mockFileOpen, mockCreateDirectories
        )

        createOrUpdateFile(self.filePath, self.fileContent)

        self.assertEqual(
            [
                call.mockGetAbsolutePath(self.filePath),
                call.mockPathExists(mockGetAbsolutePath.return_value),
                *expectedFileWriteCalls,
            ],
            mocksManager.mock_calls,
        )
        mockFileOpen.assert_called_once_with(
            mockGetAbsolutePath.return_value, mode="r+", encoding="utf-8"
        )

    @staticmethod
    def _getMockFileRead(mockFileOpen: Mock) -> Mock:
        return cast(Mock, mockFileOpen.return_value.__enter__.return_value.read)

    @staticmethod
    def _getMocksManager(
        mockGetAbsolutePath: Mock,
        mockPathExists: Mock,
        mockFileOpen: Mock,
        mockCreateDirectories: Mock,
    ) -> Mock:
        mocksManager = Mock()
        mocksManager.attach_mock(mockGetAbsolutePath, "mockGetAbsolutePath")
        mocksManager.attach_mock(mockCreateDirectories, "mockCreateDirectories")
        mocksManager.attach_mock(
            mockFileOpen.return_value.__enter__.return_value.write, "mockFileWrite"
        )
        mocksManager.attach_mock(mockPathExists, "mockPathExists")
        return mocksManager
