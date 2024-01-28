"""Contains tests for the util defined in `get_absolute_path.py`."""

# pylint: disable=missing-function-docstring

from unittest import TestCase
from unittest.mock import Mock, patch

from dotfiles.helpers.utils.get_absolute_path import getAbsolutePath


@patch("dotfiles.helpers.utils.get_absolute_path.absolutePath")
@patch("dotfiles.helpers.utils.get_absolute_path.expandUser")
@patch("dotfiles.helpers.utils.get_absolute_path.expandVars")
class GetAbsolutePathTests(TestCase):
    """Contains tests for the `getAbsolutePath` function."""

    def testIfAbsolutePathIsReturned(
        self, _mockExpandVars: Mock, _mockExpandUser: Mock, mockAbsolutePath: Mock
    ) -> None:
        filePath = "~/GitHub/dotfiles/config/settings.json"

        absoluteFilePath = getAbsolutePath(filePath)

        self.assertEqual(mockAbsolutePath.return_value, absoluteFilePath)
        mockAbsolutePath.assert_called_once()

    def testIfUserHomeAndEnvironmentVariablesAreExpanded(
        self, mockExpandVars: Mock, mockExpandUser: Mock, mockAbsolutePath: Mock
    ) -> None:
        filePath = "~/GitHub/dotfiles/config/settings.json"

        getAbsolutePath(filePath)

        mockExpandVars.assert_called_once_with(filePath)
        mockExpandUser.assert_called_once_with(mockExpandVars.return_value)
        mockAbsolutePath.assert_called_once_with(mockExpandUser.return_value)
