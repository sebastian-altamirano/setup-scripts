"""Defines a utility function to create or update a file."""

from io import TextIOWrapper
from os import makedirs as createDirectories
from os.path import exists as pathExists

from dotfiles.helpers.utils.get_absolute_path import getAbsolutePath


def createOrUpdateFile(filePath: str, content: str) -> None:
    """Creates or updates the specified file with the given content.

    Args:
        filePath: A relative or absolute path to the file, note that if the path is relative, it
            will be calculated relative to the CWD.
        content: The content to write or append to the file.
    """
    absoluteFilePath = getAbsolutePath(filePath)

    def writeContent(file: TextIOWrapper, content: str) -> None:
        file.write(content)
        if not content.endswith("\n"):
            file.write("\n")

    if pathExists(absoluteFilePath):
        with open(absoluteFilePath, mode="r+", encoding="utf-8") as file:
            fileContent = file.read()
            if not fileContent.endswith("\n") and not len(fileContent) == 0:
                file.write("\n")

            writeContent(file, content)
    else:
        createDirectories(absoluteFilePath, exist_ok=True)
        with open(absoluteFilePath, mode="w", encoding="utf-8") as file:
            writeContent(file, content)
