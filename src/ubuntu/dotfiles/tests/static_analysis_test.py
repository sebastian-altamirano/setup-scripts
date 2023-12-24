"""Contains tests for static analysis."""

from ast import FunctionDef, Module, Name, NodeVisitor
from ast import parse as parseAst
from glob import glob
from os.path import abspath as getAbsolutePath
from os.path import dirname as getDirectoryName
from os.path import join as joinPaths
from pathlib import Path
from typing import Generator, Tuple
from unittest import TestCase

from dotfiles.helpers.utils import installationStep


class InstallationStepsTests(TestCase):
    """Contains tests to perform static analysis in the installation steps."""

    @staticmethod
    def _installationStepsMetadata() -> Generator[Tuple[str, Module], None, None]:
        rootPath = getDirectoryName(getDirectoryName(getAbsolutePath(__file__)))
        scriptPaths = glob(joinPaths(rootPath, "installation_steps", "*.py"))
        installationStepPaths = [
            filePath
            for filePath in scriptPaths
            if not filePath.endswith("_test.py") and not filePath.endswith("__init__.py")
        ]

        return (
            (filePath, parseAst(Path(filePath).read_text(encoding="utf-8")))
            for filePath in installationStepPaths
        )

    def testIfAllInstallationStepsAreDecorated(self) -> None:
        """
        Checks that for all scripts located in `/installation_steps`, exactly one function is
        decorated with `installationStep`.
        """

        class InstallationStepVisitor(NodeVisitor):
            """Node visitor to count the number of functions decorated with `installationStep`."""

            def __init__(self) -> None:
                self.numberOfDecoratedFunctions = 0

            @staticmethod
            def _checkIfFunctionIsDecorated(node: FunctionDef) -> bool:
                decorators = node.decorator_list
                return any(
                    isinstance(decorator, Name) and installationStep.__name__ == decorator.id
                    for decorator in decorators
                )

            def visit_FunctionDef(self, node: FunctionDef) -> None:  # pylint: disable=invalid-name
                """Tracks the number of functions decorated with `installationStep`."""
                if self._checkIfFunctionIsDecorated(node):
                    self.numberOfDecoratedFunctions += 1

        for filePath, abstractSintaxTree in self._installationStepsMetadata():
            visitor = InstallationStepVisitor()

            visitor.visit(abstractSintaxTree)

            self.assertEqual(
                1,
                visitor.numberOfDecoratedFunctions,
                f"Exactly one function in `{filePath}` should be decorated with "
                "`installationStep`, but there "
                f"{'are' if visitor.numberOfDecoratedFunctions > 1 else 'is'}"
                f"{visitor.numberOfDecoratedFunctions}.",
            )
