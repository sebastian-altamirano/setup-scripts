"""Contains tests for the functions defined in `read_and_validate_config.py`."""

# pylint: disable=missing-function-docstring


from json import dumps as serializeDictToJsonString
from pathlib import Path
from typing import Any
from unittest import TestCase
from unittest.mock import Mock, patch

from dotfiles.read_and_validate_config import readAndValidateConfig


@patch("dotfiles.read_and_validate_config.validateJson")
@patch("dotfiles.read_and_validate_config.DOTFILES_SETTINGS_SCHEMA_FILE_PATH")
@patch("dotfiles.read_and_validate_config.DOTFILES_SETTINGS_FILE_PATH")
@patch("pathlib.Path.read_text", autospec=True)
class ReadAndValidateConfigTests(TestCase):
    """Contains tests for the `readAndValidateConfig` function."""

    def testIfConfigIsValidatedBeforeBeingReturned(
        self,
        mockPathReadText: Mock,
        _mockDotfilesSettingsFilePath: Mock,
        _mockDotfilesSettingsSchemaFilePath: Mock,
        mockValidateJson: Mock,
    ) -> None:
        settings = {"foo": "bar"}
        settingsSchema = {"foo": {"type": "string"}}

        def pathReadTextSideEffect(self: Path, *_args: Any, **_kwargs: Any) -> str:
            return serializeDictToJsonString(
                settingsSchema if "SCHEMA" in self.parts[1] else settings
            )

        mockPathReadText.side_effect = pathReadTextSideEffect

        config = readAndValidateConfig()

        mockValidateJson.assert_called_once_with(instance=settings, schema=settingsSchema)
        self.assertEqual(settings, config)
