"""Defines a utility function to warn about unsupported or unrecognized configuration keys."""

from warnings import warn

from dotfiles.helpers.constants import COLOR_TERMINATOR, YELLOW_BACKGROUND_BLACK_FOREGROUND


def warnAboutUnsupportedOrUnrecognizedConfig(key: str) -> None:
    """Issues a warning about the presence of an unsupported/unrecognized key in the configuration.

    Raises:
        ValueError: If `key` is an empty string.
    """
    if not key:
        raise ValueError("`key` cannot be an empty string.")
    warn(
        f'{YELLOW_BACKGROUND_BLACK_FOREGROUND}The configuration contains a value for "{key}", but '
        f"this key is either not recognized or is not supported by this OS.{COLOR_TERMINATOR}"
    )
