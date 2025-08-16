#!/bin/bash

# WSL Setup.
# Run this after a clean WSL installation.
# Requires restart.


CONFIG_PATH="$(realpath "$(dirname "$0")/../config")"

# Color codes
CYAN='\033[1;36m'
GREEN='\033[1;32m'
YELLOW='\033[1;33m'
RED='\033[1;31m'
COLOR_RESET='\033[0m'

info() {
	echo -e "${CYAN}Info: $*${COLOR_RESET}"
}
attention() {
	echo -e "${YELLOW}Attention: $*${COLOR_RESET}"
}
success() {
	echo -e "${GREEN}Success: $*${COLOR_RESET}"
}
error() {
	echo -e "${RED}Error: $*${COLOR_RESET}"
}


set -euo pipefail
trap 'error "An error occurred. Check the log for details."' ERR

exec > >(tee -a "$(dirname "$0")/setup.log") 2>&1

info '===== WSL Dotfiles Setup ====='
attention 'The script will install many applications and may require your attention. Please do not leave your computer unattended.\n'

# Preparatory checks.
while [[ ! -f "$CONFIG_PATH/id_ed25519" ]] || [[ ! -f "$CONFIG_PATH/id_ed25519.pub" ]]; do
	error "SSH keys not found in '$CONFIG_PATH'."
	attention 'Please copy your SSH keys ("id_ed25519" and "id_ed25519.pub") to the config directory.'
	attention 'Press Enter to retry, or Ctrl+C to abort.'
	# shellcheck disable=SC2162
	read -p '> '
done

info 'Upgrading system packages...'
sudo apt update
sudo apt upgrade -y

info 'Installing essential packages...'
sudo apt install -y \
	apt-transport-https \
	build-essential \
	curl \
	git \
	software-properties-common \
	wget

info 'Installing fish shell...'
sudo add-apt-repository -y ppa:fish-shell/release-4
sudo apt update
sudo apt install -y fish

info 'Changing the default shell to fish...'
sudo chsh -s "$(which fish)" "$(whoami)"

info 'Installing Oh My Posh...'
curl -s https://ohmyposh.dev/install.sh | bash -s

info 'Installing fish plugins...'
mkdir -p ~/.config/fish
cp "$CONFIG_PATH/fish_plugins" ~/.config/fish/fish_plugins
fish -c 'curl -sL https://raw.githubusercontent.com/jorgebucaran/fisher/main/functions/fisher.fish | source; and fisher update'

info 'Installing Node.js...'
fish -c 'nvm install lts'
fish -c 'set --universal nvm_default_version lts'
fish -c 'npm i -g npm'
fish -c 'npm i -g pnpm'

info "Installing VS Code extensions..."
extensions=(
	Angular.ng-template
	Cardinal90.multi-cursor-case-preserve
	cyrilletuzi.angular-schematics
	dbaeumer.vscode-eslint
	eamodio.gitlens
	esbenp.prettier-vscode
	GitHub.copilot
	GitHub.copilot-chat
	ms-python.python
	ms-vscode.vscode-copilot-vision
	redhat.vscode-yaml
	tamasfe.even-better-toml
	YoavBls.pretty-ts-errors
)
for extension in "${extensions[@]}"; do
	code --install-extension "$extension"
done

info 'Copying configuration files...'

# Git configuration.
cp "$CONFIG_PATH/.gitconfig" ~/.gitconfig

# SSH configuration.
mkdir -p ~/.ssh
cp "$CONFIG_PATH/ssh-config.txt" ~/.ssh/config
cp "$CONFIG_PATH/id_ed25519" ~/.ssh/id_ed25519
chmod 600 ~/.ssh/id_ed25519
cp "$CONFIG_PATH/id_ed25519.pub" ~/.ssh/id_ed25519.pub
chmod 644 ~/.ssh/id_ed25519.pub
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_ed25519

# Fish shell configuration.
mkdir -p ~/.config/fish/conf.d
cp "$CONFIG_PATH/aliases.fish" ~/.config/fish/conf.d/aliases.fish
cp "$CONFIG_PATH/config.fish" ~/.config/fish/conf.d/config.fish

# WSL configuration.
sudo cp "$CONFIG_PATH/wsl.conf" /etc/wsl.conf

# Add useful Windows binaries to PATH (`wsl.conf` removes them).
windows_binary_paths=(
	"$(which code)"
	"$(which explorer.exe)"
)
windows_paths=''
for windows_binary_path in "${windows_binary_paths[@]}"; do
	windows_paths="$windows_paths '$(dirname "$windows_binary_path")'"
done
echo "fish_add_path$windows_paths" >>~/.config/fish/conf.d/config.fish

success '\nSetup complete.'
info 'Check the README.md for the next steps.'
attention 'Press Enter to shutdown WSL.'
# shellcheck disable=SC2162
read -p '> '
wsl.exe --shutdown
