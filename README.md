# dotfiles

## Introduction

This repository contains installation scripts for Windows and Ubuntu (intended to be run on WSL).

These scripts are responsible for configuring the environment and installing and configuring the applications that I use frequently.

While all configurations are personal, the [customization section](#customization) explains some parameters that can be customized.

Since dotfiles are usually used after performing a clean OS installation, I have added documentation in `/docs` on [how to perform the installation](/docs/clean-os-install.md) and also [some things to keep in mind when assembling a computer](/docs/performance-tips.md), for when the installation is due to a hardware upgrade.

## Instructions

On a clean Windows installation, download the code from the repository and follow the instructions in the [Windows README](/src/windows/README.md). This will, among other things, install Ubuntu on WSL.

Once the installation is complete, start WSL and create a user and password for Ubuntu, copy the installation files and then follow the instructions in the [Ubuntu README](/src/ubuntu/README.md).

## Customization

You can use [`/config/settings.json`](/config/settings.json) to customize some tasks performed during the installation process without the need to modify the scripts, see [`/config/settings.schema.json`](/config/settings.schema.json) for more information.
