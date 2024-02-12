"""Contains contants."""

from os.path import join as joinPaths

from dotfiles.helpers.utils.get_absolute_path import getAbsolutePath

YELLOW_BACKGROUND_BLACK_FOREGROUND = "\x1b[6;30;43m"
GREEN_BACKGROUND_BLACK_FOREGROUND = "\x1b[6;30;42m"
COLOR_TERMINATOR = "\x1b[0m"

PROJECT_ROOT_PATH = getAbsolutePath(joinPaths(getAbsolutePath(__file__), "..", ".."))
"""Absolute path to `/src/ubuntu/dotfiles`."""
PROJECT_SCRIPTS_PATH = getAbsolutePath(joinPaths(PROJECT_ROOT_PATH, "scripts"))
"""Absolute path to `/src/ubuntu/dotfiles/scripts`."""
USER_SETTINGS_PATH = getAbsolutePath(
    joinPaths(PROJECT_ROOT_PATH, "..", "..", "..", "config", "ubuntu")
)
"""Absolute path to `/config/ubuntu`."""
DOTFILES_SETTINGS_FILE_PATH = getAbsolutePath(joinPaths(USER_SETTINGS_PATH, "..", "settings.json"))
"""Absolute path to `/config/settings.json`."""
DOTFILES_SETTINGS_SCHEMA_FILE_PATH = getAbsolutePath(
    joinPaths(USER_SETTINGS_PATH, "..", "settings.schema.json")
)
"""Absolute path to `/config/settings.schema.json`."""
