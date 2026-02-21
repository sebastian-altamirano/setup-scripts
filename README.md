# Setup Scripts

<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

## Table of Contents

- [Introduction](#introduction)
- [Formatting and Clean Install Instructions](#formatting-and-clean-install-instructions)
    - [Preparation](#preparation)
    - [BIOS](#bios)
        - [Required Before Formatting](#required-before-formatting)
        - [Optional (Can Be Enabled Later)](#optional-can-be-enabled-later)
    - [Formatting](#formatting)
- [Setup Instructions](#setup-instructions)
    - [Prerequisites](#prerequisites)
    - [Instructions](#instructions)
- [Manual Settings](#manual-settings)
    - [Windows](#windows)
- [Additional Resources](#additional-resources)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

## Introduction

This repository is designed to streamline system setup after formatting or hardware upgrades. It helps prepare the PC to the point leading to the system setup and contains setup scripts, configuration files, and optional PC building tips. While these scripts are primarily for personal use, they are shared here for anyone who might find them helpful.

**Note:** These scripts are provided as-is and may require adjustments to suit your specific needs. Please review and understand them before running.

## Formatting and Clean Install Instructions

### Preparation

- Make a list of applications to install and their installation methods (Microsoft Store, WinGet, Chocolatey, Steam, etc.). If they differ from the setup scripts, update them.
- Back up data (settings, documents, photos, videos, games, saved games, browser bookmarks, etc.).
- Download the OS ISO and create a bootable USB with Rufus using "Partition scheme: GPT" and "Target system: UEFI (non CSM)." If Rufus allows you to pre-create a local user, avoid using accents or special characters, as they may cause some applications to malfunction.
- If installing Windows, pre-download the drivers. Although Windows Update can install drivers, they are often outdated, generic, or unavailable. Save them on the bootable USB for installation after the OS.

### BIOS

Some BIOS settings are required for the formatting and setup scripts to work correctly, while others can be enabled later to optimize performance. Below, the settings are grouped for clarity:

#### Required Before Formatting

- **Update the BIOS**: This can improve boot time, system stability, security, and add support for new hardware. Ensure there are no scheduled power outages before proceeding, as interruptions during the update can brick the motherboard.
- **UEFI (Enabled)**: Must be enabled to enable Secure Boot. The boot drive must be formatted using GPT.
- **CSM (Disabled)**: Must be disabled to enable Secure Boot. The boot drive must be formatted using GPT.
- **TPM/PTT/fTPM**: Required by Secure Boot.
- **Secure Boot (Enabled)**: Required by Windows 11 and some video game anti-cheat systems.
- **Virtualization/SVM Mode (Enabled)**: Required for WSL.

#### Optional (Can Be Enabled Later)

- **Resizable BAR (Enabled)**: Improves performance in selected games.
- **Above 4G Decoding (Enabled)**: Improves performance in selected games. This is required by Resizable BAR, so enabling that setting usually enables this one.
- **XMP (Enabled)**: Required to run RAM at its advertised speed.

### Formatting

1. Update the BIOS and/or change BIOS settings if needed (e.g., for upgrading the CPU or installing Windows in UEFI mode).
2. Connect the bootable USB and give it priority in the BIOS.
3. Install the OS:
    - When choosing the Windows edition, ensure it supports the features you plan to use (WSL, virtualization, BitLocker, etc.).
    - Disable the internet connection during installation to prevent the OS from automatically installing drivers.
    - If you did not pre-create a local user with Rufus, create one now. Avoid using accents or special characters.
4. Install the drivers.
5. Install Windows and Microsoft Store updates:
    - Reconnect to the internet.
    - Log in to the Microsoft Store.
    - Download and install updates; restart the OS if required.
    - After rebooting, make sure there are no more updates pending. Some updates could disrupt the setup scripts.
6. Run the [setup scripts](#setup-instructions) to install applications and restore configurations.
7. Apply [manual settings](#manual-settings).
8. Log in to accounts.
9. Restore backups.

## Setup Instructions

### Prerequisites

Before running the scripts, make sure you meet the following requirements:

- Virtualization enabled in the BIOS: Required for WSL.
- Active internet connection: Required to download updates and applications.
- Logged-in user in the Microsoft Store: Required to install some applications with WinGet.

### Instructions

Stay attentive during the execution of the scripts, as some commands may require your input.

The scripts generate log files that you can check for errors during their execution. Each script creates a log file in the same folder as the script, with a `.log` extension.

Applications are installed using package managers, which might trigger unexpected reboots. If that happens, check the logs after the restart to determine where to resume execution. You may need to edit the scripts to skip already executed steps.

1. Download the repository as a ZIP file from GitHub.
2. Copy your GitHub SSH keys to [/config/ssh](/config/ssh).
3. Allow PowerShell scripts to run:
    1. Open PowerShell as Administrator in the repository folder.
    2. Set the execution policy to allow local scripts with `Set-ExecutionPolicy RemoteSigned -Scope CurrentUser`.
    3. Unblock the setup scripts:
        - `Unblock-File -Path .\src\windows\setup-part-1.ps1`
        - `Unblock-File -Path .\src\windows\setup-part-2.ps1`
4. Run [`/src/windows/setup-part-1.ps1`](/src/windows/setup-part-1.ps1) in an elevated PowerShell. This performs the initial configuration and will automatically reboot the PC when finished.
5. After the reboot, reopen PowerShell as Administrator and run [`/src/windows/setup-part-2.ps1`](/src/windows/setup-part-2.ps1). This will install applications, restore configurations and run the WSL setup script. This script may also trigger a reboot.
6. Apply the settings that make sense from the ["Manual settings" section](#manual-settings).

## Manual Settings

Some configurations cannot be automated. These settings are detailed below:

### Windows

- Copy the snippets from [`/src/browser-snippets`](/src/browser-snippets) [into the browser where you want to use them](https://learn.microsoft.com/en-us/microsoft-edge/devtools-guide-chromium/javascript/snippets).
- Enable 'File name extensions' and 'Hidden items' in the File Explorer options.
- Disable mouse acceleration.
- Change the mouse pointer scheme to inverted.
- Change the mouse pointer size to 3.
- Increase the text size to 150%, but leave the scale at 100%.
- Change the screen refresh rate to the maximum available value.
- Disable unwanted startup applications using Task Manager.

## Additional Resources

The [`/docs`](./docs) folder contains supplementary guides related to system setup and maintenance. While these resources are not required to run the setup scripts, they provide useful information that can help optimize your workflow and improve your overall experience.
