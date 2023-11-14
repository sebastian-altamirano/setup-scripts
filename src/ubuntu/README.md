# Ubuntu dotfiles

## Requirements

You must fill in the empty fields of [`/config/ubuntu/.gitconfig`](/config/ubuntu/.gitconfig).

## Instructions

Run [`install.sh`](./install.sh) inside WSL.

A log of the process can be found in the `~/dotfiles_install-{start_time}.log`

## Tasks performed

1. Update system dependencies.
2. Install fish.
3. Change the default shell to fish.
4. Install fisher and some plugins for it.
5. Install Node.js LTS.
6. Install Git.
7. Install VSCode extensions (some can be installed on Windows, others must be installed on WSL).
8. Import my personal settings for some applications.
9. Display post-installation instructions.
