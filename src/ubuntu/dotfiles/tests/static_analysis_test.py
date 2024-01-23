"""Contains tests for static analysis."""

from ast import (
    AST,
    Assign,
    Attribute,
    Call,
    FunctionDef,
    Import,
    ImportFrom,
    List,
    Module,
    Name,
    NodeVisitor,
)
from ast import parse as parseAst
from glob import glob
from os.path import join as joinPaths
from pathlib import Path
from typing import Any, Generator, Tuple
from unittest import TestCase

from dotfiles.helpers.utils import PROJECT_ROOT_PATH, installationStep


class InstallationStepsTests(TestCase):
    """Contains tests to perform static analysis in the installation steps."""

    @staticmethod
    def _installationStepsMetadata() -> Generator[Tuple[str, Module], None, None]:
        scriptPaths = glob(joinPaths(PROJECT_ROOT_PATH, "installation_steps", "*.py"))
        installationStepPaths = [
            filePath
            for filePath in scriptPaths
            if not filePath.endswith("_test.py") and not filePath.endswith("__init__.py")
        ]

        return (
            (filePath, parseAst(Path(filePath).read_text(encoding="utf-8")))
            for filePath in installationStepPaths
        )

    def testIfInstallationStepsAreDecorated(self) -> None:
        """
        Checks that for all scripts located in `/installation_steps`, exactly one function is
        decorated with `installationStep`.
        """

        class InstallationStepVisitor(NodeVisitor):
            """Node visitor to count the number of functions decorated with `installationStep`."""

            def __init__(self) -> None:
                self._numberOfDecoratedFunctions = 0

            @staticmethod
            def _checkIfFunctionIsDecorated(node: FunctionDef) -> bool:
                decorators = node.decorator_list
                return any(
                    isinstance(decorator, Name) and installationStep.__name__ == decorator.id
                    for decorator in decorators
                )

            def visitFunctionDef(self, node: FunctionDef) -> None:
                """Tracks the number of functions decorated with `installationStep`."""
                if self._checkIfFunctionIsDecorated(node):
                    self._numberOfDecoratedFunctions += 1

                self.generic_visit(node)

            def visit(self, node: AST) -> int:
                """Visits a node."""
                nodeName = node.__class__.__name__
                visitor = getattr(self, f"visit{nodeName}", self.generic_visit)
                visitor(node)

                return self._numberOfDecoratedFunctions

        for filePath, abstractSintaxTree in self._installationStepsMetadata():
            visitor = InstallationStepVisitor()

            numberOfDecoratedFunctions = visitor.visit(abstractSintaxTree)

            self.assertEqual(
                1,
                numberOfDecoratedFunctions,
                f"Exactly one function in `{filePath}` should be decorated with `installationStep`,"
                f" but there {'are' if numberOfDecoratedFunctions > 1 else 'is'} "
                f"{numberOfDecoratedFunctions}.",
            )

    def testIfInstallationStepsDoNotUseSubprocessRun(self) -> None:
        """
        Checks that for all scripts located in `/installation_steps`, `subprocess.run` is not being
        used directly.
        """

        class InstallationStepVisitor(NodeVisitor):
            """Node visitor to check if `subprocess.run` is being used."""

            def __init__(self) -> None:
                self._isUsingSubprocess = False
                self._isUsingSubprocessRun = False

            def _checkIfTheAssignmentIsSubprocessRun(self, node: Attribute) -> bool:
                return (
                    isinstance(node.value, Name)
                    and node.value.id == "subprocess"
                    and node.attr == "run"
                )

            def visitAssign(self, node: Assign) -> Any:
                """Checks if `subprocess.run` is being assigned to a variable."""
                if not self._isUsingSubprocess:
                    return

                if (
                    isinstance(node.value, Attribute)
                    and self._checkIfTheAssignmentIsSubprocessRun(node.value)
                ) or (
                    isinstance(node.value, List)
                    and any(
                        isinstance(subNode, Attribute)
                        and self._checkIfTheAssignmentIsSubprocessRun(subNode)
                        for subNode in node.value.elts
                    )
                ):
                    self._isUsingSubprocessRun = True
                    raise StopIteration()

            def visitCall(self, node: Call) -> None:
                """Checks if `subprocess.run` is being called."""
                if not self._isUsingSubprocess:
                    return

                if (
                    isinstance(node.func, Attribute)
                    and isinstance(node.func.value, Name)
                    and node.func.value.id == "subprocess"
                    and node.func.attr == "run"
                ):
                    self._isUsingSubprocessRun = True
                    raise StopIteration()

                self.generic_visit(node)

            def visitImportFrom(self, node: ImportFrom) -> None:
                """Checks if `subprocess.run` is being imported."""
                if node.module == "subprocess" and any(
                    importName.name == "run" for importName in node.names
                ):
                    self._isUsingSubprocessRun = True
                    raise StopIteration()

            def visitImport(self, node: Import) -> None:
                """Checks if `subprocess` is being imported."""
                if any(importName.name == "subprocess" for importName in node.names):
                    self._isUsingSubprocess = True

            def visit(self, node: AST) -> bool:
                """Visits a node."""
                nodeName = node.__class__.__name__
                visitor = getattr(self, f"visit{nodeName}", self.generic_visit)

                try:
                    visitor(node)
                except StopIteration:
                    pass

                return self._isUsingSubprocessRun

        for filePath, abstractSintaxTree in self._installationStepsMetadata():
            visitor = InstallationStepVisitor()

            isUsingSubprocessRun = visitor.visit(abstractSintaxTree)

            self.assertFalse(
                isUsingSubprocessRun,
                f"`{filePath}` makes use of `subprocess.run`, replace it with `runWithSh` or "
                "`runWithFish`.",
            )
