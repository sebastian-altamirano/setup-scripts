# Windows dotfiles

## Requirements

You must enable "virtualization" in the BIOS in order to enable Hyper-V, which is required to install WSL.

## Instructions

Run [`install.ps1`](./install.ps1) as administrator on a clean Windows installation. The computer will reboot a few times during the process. When finished, a series of post-installation steps will be printed out for you to follow.

A log of the process can be found in the `dotfiles-install-{start_time}.log` file inside `My Documents`.

## Tasks performed

### [`install.ps1`](./install.ps1)

1. Install the latest version of PowerShell.
2. Run [`install-part-1.ps1`](./install-part-1.ps1) using the latest version of PowerShell.

### [`install-part-1.ps1`](./install-part-1.ps1)

1. [Install the Dotfiles's module for PowerShell](./Dotfiles/Dotfiles.psd1). It contains a few utility functions that will be used throughout the installation process.
2. Enable Hyper-V.
3. Create a scheduled task to run [`install-part-2.ps1`](./install-part-2.ps1) the next time the computer is turned on.
4. Restart the computer.

### [`install-part-2.ps1`](./install-part-2.ps1)

1. Install Ubuntu on WSL2.
2. Create a scheduled task to run [`install-part-3.ps1`](./install-part-3.ps1) the next time the computer is turned on.
3. Restart the computer.

### [`install-part-3.ps1`](./install-part-3.ps1)

1. Install applications using winget.
2. Install VSCode extensions.
3. Uninstall Cortana.
4. Create folders and quick access links.
5. Import my personal Windows settings.
6. Import my personal settings for some applications.
7. Download fonts.
8. Display post-installation instructions.
