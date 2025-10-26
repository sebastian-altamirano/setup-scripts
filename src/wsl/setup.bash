#!/bin/bash

# WSL Setup.
# Run this after a clean WSL installation.
# Requires restart.

set -euo pipefail

CONFIG_PATH="$(realpath "$(dirname "$0")/../config")"

# Color codes
CYAN='\033[1;36m'
GREEN='\033[1;32m'
YELLOW='\033[1;33m'
RED='\033[1;31m'
COLOR_RESET='\033[0m'

print_info() {
	echo -e "${CYAN}Info: $*${COLOR_RESET}"
}
print_attention() {
	echo -e "${YELLOW}Attention: $*${COLOR_RESET}"
}
print_success() {
	echo -e "${GREEN}Success: $*${COLOR_RESET}"
}
print_error() {
	echo -e "${RED}Error: $*${COLOR_RESET}"
}

LOG_PATH="$(readlink -f "$(dirname "$0")/wsl-setup.log")"
handle_error() {
	print_error "WSL setup failed.\nCheck the log for details: '$LOG_PATH'."
}
trap handle_error ERR

cleanup() {
	if [[ -n "${SUDO_REFRESH_PID:-}" ]]; then
		kill "$SUDO_REFRESH_PID" 2>/dev/null || true
	fi
}
trap cleanup EXIT

exec > >(tee -a "$LOG_PATH") 2>&1

print_info '===== WSL Setup ====='
print_attention 'The script will install many applications and may require your attention.' \
	'Please do not leave your computer unattended.'

# Preparatory checks.
while [[ ! -f "$CONFIG_PATH/id_ed25519" ]] || [[ ! -f "$CONFIG_PATH/id_ed25519.pub" ]]; do
	print_error "SSH keys not found in '$CONFIG_PATH'."
	print_attention 'Please copy your SSH keys ('\''id_ed25519'\'' and '\''id_ed25519.pub'\'') to' \
		'the config directory.'
	print_attention 'Press Enter to retry, or Ctrl+C to abort.'
	# shellcheck disable=SC2162
	read -p '> '
done

print_info 'Requesting sudo permissions...'
sudo -v
# Refresh `sudo` in the background.
while true; do
	sudo -n true 2>/dev/null || true
	sleep 60
done &
SUDO_REFRESH_PID=$!

print_info 'Fixing timezone...'
sudo ln -sf /usr/share/zoneinfo/America/Argentina/Buenos_Aires /etc/localtime

print_info 'Upgrading system packages...'
sudo apt update
sudo apt upgrade -y

print_info 'Installing APT packages...'
sudo apt install -y \
	apt-transport-https \
	build-essential \
	curl \
	eza \
	git \
	software-properties-common \
	unzip \
	wget

print_info 'Installing fish shell...'
sudo add-apt-repository -y ppa:fish-shell/release-4
sudo apt update
sudo apt install -y fish

print_info 'Changing the default shell to fish...'
sudo chsh -s "$(which fish)" "$(whoami)"

print_info 'Installing Oh My Posh...'
curl -s https://ohmyposh.dev/install.sh | bash -s

print_info 'Installing fish plugins...'
mkdir -p ~/.config/fish
cp "$CONFIG_PATH/fish_plugins" ~/.config/fish/fish_plugins
FISHER_INSTALLER='https://raw.githubusercontent.com/jorgebucaran/fisher/main/functions/fisher.fish'
fish --no-config -c "curl -sL $FISHER_INSTALLER | source; and fisher update"

print_info 'Installing Node.js...'
fish --no-config -c 'nvm install lts'
fish --no-config -c 'set --universal nvm_default_version lts'
fish --no-config -c 'nvm use lts; npm i -g npm; npm i -g pnpm'

print_info "Installing VS Code extensions..."
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

print_info 'Copying configuration files...'

print_info 'Copying Git configuration...'
cp "$CONFIG_PATH/.gitconfig" ~/.gitconfig

print_info 'Copying SSH configuration...'
mkdir -p ~/.ssh
chmod 700 ~/.ssh
cp "$CONFIG_PATH/ssh-config.txt" ~/.ssh/config
chmod 600 ~/.ssh/config
cp "$CONFIG_PATH/id_ed25519" ~/.ssh/id_ed25519
chmod 600 ~/.ssh/id_ed25519
cp "$CONFIG_PATH/id_ed25519.pub" ~/.ssh/id_ed25519.pub
chmod 644 ~/.ssh/id_ed25519.pub
# Add GitHub's SSH key to `known_hosts`.
ssh-keyscan -t ed25519 github.com >>~/.ssh/known_hosts
chmod 644 ~/.ssh/known_hosts

print_info 'Copying Fish shell configuration...'
mkdir -p ~/.config/fish/conf.d
cp "$CONFIG_PATH/aliases.fish" ~/.config/fish/conf.d/aliases.fish
cp "$CONFIG_PATH/config.fish" ~/.config/fish/conf.d/config.fish

print_info 'Copying WSL configuration...'
sudo cp "$CONFIG_PATH/wsl.conf" /etc/wsl.conf

print_info 'Configuring PATH...'
# Add local + selected Windows binary directories to fish's PATH (`wsl.conf` disables Windows PATH
# injection for stability reasons).
fish_paths=("$HOME/.local/bin")
windows_binaries=(
	'code'
	'explorer.exe'
)
for windows_binary in "${windows_binaries[@]}"; do
	fish_paths+=("$(dirname "$(which "$windows_binary")")")
done
quoted_fish_paths=()
for fish_path in "${fish_paths[@]}"; do
	quoted_fish_paths+=("'$fish_path'")
done
echo "fish_add_path ${quoted_fish_paths[*]}" >>~/.config/fish/conf.d/config.fish

# This is needed to access Windows user profile paths from WSL.
# It allows sharing the Oh My Posh configuration between WSL and Windows without duplication.
# Storing the username instead of the full profile path lets you build other paths dynamically, like
# AppData.
print_info 'Setting universal fish variable: windows_username'
# shellcheck disable=SC2016
fish --no-config -c 'set --universal windows_username (pwsh.exe -NoProfile -Command '\''echo $env:UserName'\'' | string trim)'

print_success '\nSetup complete.'
print_info 'Check the '\''README.md'\'' for the next steps.'
print_attention 'Press Enter to shutdown WSL.'
# shellcheck disable=SC2162
read -p '> '
wsl.exe --shutdown
