"""Contains tests for the util defined in `copy_configuration.py`."""

# pylint: disable=missing-function-docstring

from unittest import TestCase
from unittest.mock import Mock, call, patch

from dotfiles.helpers.utils.copy_configuration import copyConfiguration


@patch("dotfiles.helpers.utils.copy_configuration.copyFile")
@patch("dotfiles.helpers.utils.copy_configuration.createDirectories")
@patch("dotfiles.helpers.utils.copy_configuration.copyDirectory")
@patch("dotfiles.helpers.utils.copy_configuration.isDirectory")
@patch("dotfiles.helpers.utils.copy_configuration.pathExists")
@patch("dotfiles.helpers.utils.copy_configuration.getAbsolutePath")
@patch("dotfiles.helpers.utils.copy_configuration.joinPaths")
class CopyConfigurationTests(TestCase):
    """Contains tests for the `copyConfiguration` function."""

    def testIfFileIsCopied(  # pylint: disable=too-many-arguments
        self,
        mockJoinPaths: Mock,
        mockGetAbsolutePath: Mock,
        mockPathExists: Mock,
        mockIsDirectory: Mock,
        mockCopyDirectory: Mock,
        mockCreateDirectories: Mock,
        mockCopyFile: Mock,
    ) -> None:
        fileName = ".gitconfig"
        absoluteSourcePath = f"/home/sebastian/GitHub/dotfiles/config/ubuntu/{fileName}"
        mockJoinPaths.return_value = absoluteSourcePath
        destinationPath = "~/.gitconfig"
        absoluteDestinationPath = f"/home/sebastian/{destinationPath[2:]}"
        mockGetAbsolutePath.return_value = absoluteDestinationPath
        mockPathExists.return_value = True
        mockIsDirectory.return_value = False
        mocksManager = Mock()
        mocksManager.attach_mock(mockCreateDirectories, "mockCreateDirectories")
        mocksManager.attach_mock(mockCopyFile, "mockCopyFile")

        copyConfiguration(fileName, destinationPath)

        mockCopyDirectory.assert_not_called()
        self.assertEqual(
            [
                call.mockCreateDirectories(absoluteDestinationPath, exist_ok=True),
                call.mockCopyFile(src=absoluteSourcePath, dst=absoluteDestinationPath),
            ],
            mocksManager.mock_calls,
        )

    def testIfDirectoryIsCopied(  # pylint: disable=too-many-arguments
        self,
        mockJoinPaths: Mock,
        mockGetAbsolutePath: Mock,
        mockPathExists: Mock,
        mockIsDirectory: Mock,
        mockCopyDirectory: Mock,
        mockCreateDirectories: Mock,
        mockCopyFile: Mock,
    ) -> None:
        directoryName = "fish"
        absoluteSourcePath = f"/home/sebastian/GitHub/dotfiles/config/ubuntu/{directoryName}"
        mockJoinPaths.return_value = absoluteSourcePath
        destinationPath = "~/.config/fish"
        absoluteDestinationPath = f"/home/sebastian/{destinationPath[2:]}"
        mockGetAbsolutePath.return_value = absoluteDestinationPath
        mockPathExists.return_value = True
        mockIsDirectory.return_value = True

        copyConfiguration(directoryName, destinationPath)

        mockCreateDirectories.assert_not_called()
        mockCopyFile.assert_not_called()
        mockCopyDirectory.assert_called_once_with(
            src=absoluteSourcePath, dst=absoluteDestinationPath, dirs_exist_ok=True
        )

    def testIfResourceCannotBeANonExistentResource(
        self,
        _mockJoinPaths: Mock,
        _mockGetAbsolutePath: Mock,
        mockPathExists: Mock,
        _mockIsDirectory: Mock,
        _mockCopyDirectory: Mock,
        _mockCreateDirectories: Mock,
        _mockCopyFile: Mock,
    ) -> None:
        nonExistentResource = "asdasdsa"
        destinationPath = '~/.config/fish"'
        mockPathExists.return_value = False

        with self.assertRaises(FileNotFoundError):
            copyConfiguration(nonExistentResource, destinationPath)
