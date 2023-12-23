"""This module contains the installation steps that make up the Dotfiles."""

from .configure_git import configureGit
from .copy_application_settings import copyApplicationSettings
from .install_fish import installFish
from .install_packages import installPackages
from .install_vscode_extensions import installVSCodeExtensions
from .upgrade_system_dependencies import upgradeSystemDependencies

__all__ = [
    "configureGit",
    "copyApplicationSettings",
    "installFish",
    "installPackages",
    "installVSCodeExtensions",
    "upgradeSystemDependencies",
]
