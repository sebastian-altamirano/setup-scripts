# dotfiles

## Introduction

This repository contains installation scripts for Windows and Linux (intended to be run on WSL).

These scripts are responsible for configuring the environment and installing and configuring the applications that I use frequently.

While all configurations are personal, the [customization section](#customization) explains some parameters that can be customized.

## Instructions

On a clean Windows installation, clone the repository and follow the instructions in the [Windows installation script section](#windows-installation-script). This will, among other things, install Linux on WSL.

Once the installation is complete, create a user and password for Linux, copy the installation files, and then follow the instructions in the [Linux installation script section](#linux-installation-script).

## Windows installation script

Run `windows/install.ps1` as administrator on a clean Windows installation. The computer will reboot a few times during the process. When finished, a series of post-installation steps will be printed out for you to follow.

A log of the process can be found in the `dotfiles-install.log` file inside `My Documents`.

### Requirements

You must enable "virtualization" in the BIOS in order to enable Hyper-V, which is required to install WSL.

### Tasks performed

#### `windows/install.ps1`

1. Install the latest version of PowerShell.
2. Run `windows/install-part-1.ps1` using the latest version of PowerShell.

#### `windows/install-part-1.ps1`

1. [Install the Dotfiles's module for PowerShell](https://github.com/sebastian-altamirano/dotfiles/tree/main/windows/Dotfiles). It contains a few utility functions that will be used throughout the installation process.
2. Enable Hyper-V.
3. Create a scheduled task to run `windows/install-part-2.ps1` the next time the computer is turned on.
4. Restart the computer.

#### `windows/install-part-2.ps1`

1. Install Ubuntu on WSL2.
2. Create a scheduled task to run `windows/install-part-3.ps1` the next time the computer is turned on.
3. Restart the computer.

#### `windows/3-install-apps-and-settings.ps1`

1. Install applications using winget.
2. Install VSCode extensions.
3. Uninstall Cortana.
4. Create folders and quick access links.
5. Import my personal Windows settings.
6. Import my personal settings for some applications.
7. Create scheduled tasks.
8. Download fonts.
9. Display post-installation instructions.

## Linux installation script

This script is intended to be run on Ubuntu running inside WSL.

### Requirements

You must fill in the empty fields of `linux/app-settings/.gitconfig`.

### Tasks performed

### `linux/install.sh`

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

In both `/windows` and `/linux` we can find the `/config` and `/app-settings` directories, which we can use to customize some tasks performed during the installation process without the need to modify the scripts.

### `/config`

It contains configuration files that are used during the installation process and have no use once the installation is complete.

### `app-settings`

Some applications store their settings inside one or several files. The purpose of this folder is to store these settings so that they can be copied to their destination path during the installation process.

The `settings-paths.json` file, located inside `/config`, stores the source resource name and the destination path of these settings. On Windows the value of `destination` may include PowerShell environment variables, such as `$env:AppData`.
