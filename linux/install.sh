#!/bin/bash

# Upgrade system dependencies.
sudo apt update
sudo apt -y upgrade

# Install fish.
sudo apt-add-repository -y ppa:fish-shell/release-3
sudo apt -y install fish

# Change the default shell to fish.
chsh -s $(which fish)

# Install fisher and some plugins for it.
fish -c " \
	curl -sL https://raw.githubusercontent.com/jorgebucaran/fisher/main/functions/fisher.fish | source && \
	fisher install jorgebucaran/fisher && \
	fisher install IlanCosman/tide@v5 && \
	fisher install jethrokuan/z && \
	fisher install jorgebucaran/nvm.fish \
"

# Install Node LTS.
fish -c "
	nvm install lts && \
	npm i -g npm \
	set --universal nvm_default_version lts \
"

# Install Git.
sudo apt -y install git

# Install VSCode extensions.
while read extension; do
  code --install-extension $extension
done <config/vscode-extensions.txt

# Copy application settings.
python3 copy-application-settings.py

# Show post-install instructions.
echo "$(tput setab 2)Finished!"
echo "Now there are some manual steps you need to perform:"
echo "- Run `tide configure` to configure the aspect of fish."

fish
