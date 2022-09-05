#!/usr/bin/env fish

# Upgrade system dependencies.
sudo apt update
sudo apt -y upgrade

# Install fisher and some plugins for it.
curl -sL https://git.io/fisher | source && fisher install jorgebucaran/fisher
fisher install IlanCosman/tide@v5
fisher install jethrokuan/z
fisher install jorgebucaran/nvm.fish

# Install Node LTS.
nvm install lts
npm i -g npm
set --universal nvm_default_version lts

# Install Git.
sudo apt -y install git

# Install VSCode extensions.
python3 install-vscode-extensions.py

# Copy application settings.
python3 copy-application-settings.py

# Restart GPG Agent for its configuration to take effect.
gpg-connect-agent reloadagent /bye

# Show post-install instructions.
echo "$(tput setab 2)Finished!"
echo "Now there are some manual steps you need to perform:"
echo "- Run `tide configure` to configure the aspect of fish."

fish
