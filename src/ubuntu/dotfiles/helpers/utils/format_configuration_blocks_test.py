"""Contains tests for the util defined in `format_configuration_blocks.py`."""

# pylint: disable=missing-function-docstring

from typing import List
from unittest import TestCase

from dotfiles.helpers.utils.format_configuration_blocks import formatConfigurationBlocks


class FormatConfigurationBlocksTests(TestCase):
    """Contains tests for the `formatConfigurationBlocks` function."""

    def testIfConfigurationBlocksAreFormattedCorrectly(self) -> None:
        configurationBlocks = [
            [
                "# Cache the password for 10 hours.",
                "cache-password true",
                "cache-password-time 36000",
            ],
            ["# Allow committing from VSCode.", "allow-commiting-from-vscode true"],
        ]

        formattedConfigurationBlocks = formatConfigurationBlocks(configurationBlocks)

        self.assertEqual(
            (
                f"{configurationBlocks[0][0]}\n"
                f"{configurationBlocks[0][1]}\n"
                f"{configurationBlocks[0][2]}\n\n"
                f"{configurationBlocks[1][0]}\n"
                f"{configurationBlocks[1][1]}\n"
            ),
            formattedConfigurationBlocks,
        )

    def testIfEmptyBlocksAreFilteredOut(self) -> None:
        configurationBlocks: List[List[str]] = [
            [],
            ["# Allow committing from VSCode.", "allow-commiting-from-vscode true"],
        ]

        formattedConfigurationBlocks = formatConfigurationBlocks(configurationBlocks)

        self.assertEqual(
            (f"{configurationBlocks[1][0]}\n" f"{configurationBlocks[1][1]}\n"),
            formattedConfigurationBlocks,
        )

    def testIfAnEmptyStringIsReturnedIfThereAreNoBlocks(self) -> None:
        configurationBlocks: List[List[str]] = []

        formattedConfigurationBlocks = formatConfigurationBlocks(configurationBlocks)

        self.assertEqual("", formattedConfigurationBlocks)
