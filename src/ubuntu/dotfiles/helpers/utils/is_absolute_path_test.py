"""Contains tests for the util defined in `is_absolute_path.py`."""

# pylint: disable=missing-function-docstring

from unittest import TestCase
from unittest.mock import Mock, patch

from dotfiles.helpers.utils.is_absolute_path import isAbsolutePath


@patch("dotfiles.helpers.utils.is_absolute_path.isAbsolute")
@patch("dotfiles.helpers.utils.is_absolute_path.expandUser")
@patch("dotfiles.helpers.utils.is_absolute_path.expandVars")
class IsAbsolutePathTests(TestCase):
    """Contains tests for the `isAbsolutePath` function."""

    def testIfTheCheckIsPerformed(
        self, _mockExpandVars: Mock, _mockExpandUser: Mock, mockIsAbsolute: Mock
    ) -> None:
        filePath = "~/GitHub/dotfiles/config/settings.json"

        absoluteFilePath = isAbsolutePath(filePath)

        self.assertEqual(mockIsAbsolute.return_value, absoluteFilePath)
        mockIsAbsolute.assert_called_once()

    def testIfUserHomeAndEnvironmentVariablesAreExpanded(
        self, mockExpandVars: Mock, mockExpandUser: Mock, mockIsAbsolute: Mock
    ) -> None:
        filePath = "~/GitHub/dotfiles/config/settings.json"

        isAbsolutePath(filePath)

        mockExpandVars.assert_called_once_with(filePath)
        mockExpandUser.assert_called_once_with(mockExpandVars.return_value)
        mockIsAbsolute.assert_called_once_with(mockExpandUser.return_value)
