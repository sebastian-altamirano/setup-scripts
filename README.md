# dotfiles

## Introduction

This repository contains installation scripts for Windows and Ubuntu (intended to be run on WSL).

These scripts are responsible for configuring the environment and installing and configuring the applications that I use frequently.

While all configurations are personal, the [customization section](#customization) explains some parameters that can be customized.

Since dotfiles are usually used after performing a clean OS installation, I have added documentation in `/docs` on [how to perform the installation](/docs/clean-os-install.md) and also [some things to keep in mind when assembling a computer](/docs/performance-tips.md), for when the installation is due to a hardware upgrade.

## Instructions

On a clean Windows installation, clone the repository and follow the instructions in the [Windows installation script section](#windows-installation-script). This will, among other things, install Ubuntu on WSL.

Once the installation is complete, create a user and password for Ubuntu, copy the installation files, and then follow the instructions in the [Ubuntu installation script section](#ubuntu-installation-script).

## Windows installation script

Run `/src/windows/install.ps1` as administrator on a clean Windows installation. The computer will reboot a few times during the process. When finished, a series of post-installation steps will be printed out for you to follow.

A log of the process can be found in the `dotfiles-install.log` file inside `My Documents`.

### Requirements

You must enable "virtualization" in the BIOS in order to enable Hyper-V, which is required to install WSL.

### Tasks performed

#### `/src/windows/install.ps1`

1. Install the latest version of PowerShell.
2. Run `/src/windows/install-part-1.ps1` using the latest version of PowerShell.

#### `/src/windows/install-part-1.ps1`

1. [Install the Dotfiles's module for PowerShell](https://github.com/sebastian-altamirano/dotfiles/tree/main/windows/Dotfiles). It contains a few utility functions that will be used throughout the installation process.
2. Enable Hyper-V.
3. Create a scheduled task to run `/src/windows/install-part-2.ps1` the next time the computer is turned on.
4. Restart the computer.

#### `/src/windows/install-part-2.ps1`

1. Install Ubuntu on WSL2.
2. Create a scheduled task to run `/src/windows/install-part-3.ps1` the next time the computer is turned on.
3. Restart the computer.

#### `/src/windows/install-part-3.ps1`

1. Install applications using winget.
2. Install VSCode extensions.
3. Uninstall Cortana.
4. Create folders and quick access links.
5. Import my personal Windows settings.
6. Import my personal settings for some applications.
7. Download fonts.
8. Display post-installation instructions.

## Ubuntu installation script

This script is intended to be run inside WSL.

### Requirements

You must fill in the empty fields of `/config/ubuntu/.gitconfig`.

### Tasks performed

### `/src/ubuntu/install.sh`

1. Update system dependencies.
2. Install fish.
3. Change the default shell to fish.
4. Install fisher and some plugins for it.
5. Install Node.js LTS.
6. Install Git.
7. Install VSCode extensions (some can be installed on Windows, others must be installed on WSL).
8. Import my personal settings for some applications.
9. Display post-installation instructions.

## Customization

You can use `/config/settings.json` to customize some tasks performed during the installation process without the need to modify the scripts, see `/config/settings.schema.json` for more information.
