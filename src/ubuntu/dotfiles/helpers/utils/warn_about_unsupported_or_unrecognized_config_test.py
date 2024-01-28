"""Contains tests for the util defined in `warn_about_unsupported_or_unrecognized_config.py`."""

# pylint: disable=missing-function-docstring

from unittest import TestCase
from unittest.mock import Mock, patch

from dotfiles.helpers.utils.warn_about_unsupported_or_unrecognized_config import (
    warnAboutUnsupportedOrUnrecognizedConfig,
)


class WarnAboutUnsupportedOrUnrecognizedConfigTests(TestCase):
    """Contains tests for the `warnAboutUnsupportedOrUnrecognizedConfig`function."""

    @patch("dotfiles.helpers.utils.warn_about_unsupported_or_unrecognized_config.warn")
    def testIfAWarningIsIssued(self, mockWarn: Mock) -> None:
        yellowBackgroundBlackForeground = "\x1b[6;30;43m"
        colorTerminator = "\x1b[0m"
        key = "quickAccessFolders"

        warnAboutUnsupportedOrUnrecognizedConfig(key)

        mockWarn.assert_called_once_with(
            f'{yellowBackgroundBlackForeground}The configuration contains a value for "{key}", but '
            f"this key is either not recognized or is not supported by this OS.{colorTerminator}"
        )

    def testIfKeyCannotBeAnEmptyString(self) -> None:
        key = ""

        with self.assertRaisesRegex(ValueError, "`key` cannot be an empty string."):
            warnAboutUnsupportedOrUnrecognizedConfig(key)
