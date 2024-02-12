"""Defines a function that reads and validates the configuration file."""

from json import loads as readJson
from pathlib import Path

from jsonschema import ValidationError
from jsonschema import validate as validateJson

from dotfiles.helpers.constants import (
    DOTFILES_SETTINGS_FILE_PATH,
    DOTFILES_SETTINGS_SCHEMA_FILE_PATH,
)
from dotfiles.type_definitions import Config


def readAndValidateConfig() -> Config:
    """Reads and validates the configuration file.

    Raises:
        ValidationError: If the validation of `settings.json` with `settings.schema.json` fails.
    """
    config: Config = readJson(Path(DOTFILES_SETTINGS_FILE_PATH).read_text(encoding="utf-8"))
    configSchema = readJson(Path(DOTFILES_SETTINGS_SCHEMA_FILE_PATH).read_text(encoding="utf-8"))

    try:
        validateJson(instance=config, schema=configSchema)
    except ValidationError as error:
        raise ValidationError(
            "Failed to validate `settings.json` with `settings.schema.json`, fix the errors and "
            "try again."
        ) from error

    return config
