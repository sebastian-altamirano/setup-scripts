"""Defines a utility function for formatting text blocks."""

from typing import List


def formatConfigurationBlocks(configurationBlocks: List[List[str]]) -> str:
    """Formats the given configuration blocks into a single string."""
    filteredConfigurationBlocks = [
        configurationBlock
        for configurationBlock in configurationBlocks
        if configurationBlock
        if len(configurationBlock) > 0
    ]

    if len(filteredConfigurationBlocks) == 0:
        return ""

    return (
        "\n\n".join(
            ["\n".join(configurationBlock) for configurationBlock in filteredConfigurationBlocks]
        )
        + "\n"
    )
