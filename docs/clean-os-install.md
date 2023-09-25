# Clean operating system installation

Dotfiles are commonly used to restore personal settings after performing a clean install of the operating system, it is because of this close relationship between the two that I decided to put together instructions for when you want to perform an installation of this type.

The instructions were written with Windows in mind, but the steps should not vary too much when installing other operating systems.

## Formatting requirements

-   Make a backup.
    -   In the cloud.
    -   On an external storage device.
    -   On a borrowed internal storage unit or one that we are not going to format.
-   Create a bootable USB with the operating system you want to install:
    1.  Download the ISO of the operating system.
    2.  Create a bootable USB with Rufus. If the motherboard supports UEFI, then the following options can be used:
        -   Partition scheme: GPT.
        -   Target system: UEFI (non CSM).
        -   File system: FAT32.
-   Download the drivers and store them on a USB stick - for this you can use the same USB stick that was used to create the bootable USB -:
    -   Ethernet.
    -   GPU.
    -   Chipset.
    -   Audio.
    -   Wireless network adapter.
    -   Peripherals.
    -   Others.

Although the drivers can be downloaded from Windows Update, it may happen that:

-   Not all of them are available.
-   Some are outdated.
-   Some are generic versions.

This is why it is usually preferable to install the drivers manually.

## Steps to format and install the operating system

1.  Disconnect the computer from the Internet before starting the process, this is to prevent Windows Update from trying to install the drivers automatically, since we are going to install them manually.
2.  Connect the bootable USB and put it first in the priority list inside the BIOS.
3.  Create the partitions you want and install the operating system.
    -   When prompted to enter a user name, do not use accents or special characters, as some programs may not work properly.
    -   An internet connection is required to validate the license, but this can be done after installation.
4.  Install the drivers you downloaded in advance.
5.  Connect the computer to the Internet.
6.  Install the dotfiles.
7.  Restore the backups.
