#!/bin/bash

# Install fish.
sudo apt-add-repository -y ppa:fish-shell/release-3
sudo apt -y install fish

# Change the default shell to fish.
chsh -s $(which fish)
