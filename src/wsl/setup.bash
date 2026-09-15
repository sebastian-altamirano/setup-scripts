#!/bin/bash

# WSL Setup.
# Run this after a clean WSL installation.
# Requires restart.

set -euo pipefail

CONFIG_PATH="$(realpath "$(dirname "$0")/../../config")"

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
SRC_SSH_DIR="$CONFIG_PATH/ssh"
SRC_SSH_PRIVATE_KEY="$SRC_SSH_DIR/id_ed25519"
SRC_SSH_PUBLIC_KEY="$SRC_SSH_DIR/id_ed25519.pub"

while [[ ! -f "$SRC_SSH_PRIVATE_KEY" ]] || [[ ! -f "$SRC_SSH_PUBLIC_KEY" ]]; do
	print_error "SSH keys not found in '$SRC_SSH_DIR'."
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
	bat \
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
FISH_CONFIG_HOME="$HOME/.config/fish"
mkdir -p "$FISH_CONFIG_HOME"
cp "$CONFIG_PATH/fish/fish_plugins" "$FISH_CONFIG_HOME/fish_plugins"
FISHER_INSTALLER='https://raw.githubusercontent.com/jorgebucaran/fisher/main/functions/fisher.fish'
fish --no-config -c "curl -sL $FISHER_INSTALLER | source; and fisher update"

print_info 'Installing Node.js...'
fish --no-config -c 'nvm install lts'
fish --no-config -c 'set --universal nvm_default_version lts'
fish --no-config -c 'nvm use lts; npm i -g npm; npm i -g pnpm'

print_info "Installing VS Code extensions..."
EXTENSIONS=(
	Angular.ng-template
	Cardinal90.multi-cursor-case-preserve
	cyrilletuzi.angular-schematics
	dbaeumer.vscode-eslint
	esbenp.prettier-vscode
	GitHub.copilot
	GitHub.copilot-chat
	ms-python.python
	ms-vscode.vscode-copilot-vision
	redhat.vscode-yaml
	tamasfe.even-better-toml
	YoavBls.pretty-ts-errors
)
for extension in "${EXTENSIONS[@]}"; do
	code --install-extension "$extension"
done

print_info 'Copying configuration files...'

print_info 'Copying Git configuration...'
cp "$CONFIG_PATH/git/.gitconfig" ~/.gitconfig

print_info 'Copying SSH configuration...'
DEST_SSH_DIR="$HOME/.ssh"
mkdir -p "$DEST_SSH_DIR"
chmod 700 "$DEST_SSH_DIR"
SSH_CONFIG="$DEST_SSH_DIR/config"
cp "$SRC_SSH_DIR/config" "$SSH_CONFIG"
chmod 600 "$SSH_CONFIG"
cp "$SRC_SSH_PRIVATE_KEY" "$DEST_SSH_DIR/id_ed25519"
chmod 600 "$DEST_SSH_DIR/id_ed25519"
cp "$SRC_SSH_PUBLIC_KEY" "$DEST_SSH_DIR/id_ed25519.pub"
chmod 644 "$DEST_SSH_DIR/id_ed25519.pub"
# Add GitHub's SSH key to `known_hosts`.
SSH_KNOWN_HOSTS="$DEST_SSH_DIR/known_hosts"
ssh-keyscan -t ed25519 github.com >>"$SSH_KNOWN_HOSTS"
chmod 644 "$SSH_KNOWN_HOSTS"

print_info 'Copying Fish shell configuration...'
FISH_CONFD_DIR="$FISH_CONFIG_HOME/conf.d"
mkdir -p "$FISH_CONFD_DIR"
SRC_FISH_CONF_DIR="$CONFIG_PATH/fish/conf.d"
FISH_CONF_FILES=(aliases.fish functions.fish config.fish)
for file in "${FISH_CONF_FILES[@]}"; do
	cp "$SRC_FISH_CONF_DIR/$file" "$FISH_CONFD_DIR/$file"
done

print_info 'Copying WSL configuration...'
sudo cp "$CONFIG_PATH/wsl/wsl.conf" /etc/wsl.conf

# `wsl.conf` disables Windows PATH injection for stability reasons.
print_info 'Adding Windows binaries to PATH...'
LOCAL_BIN_DIR="$HOME/.local/bin"
mkdir -p "$LOCAL_BIN_DIR"
WINDOWS_BINARIES=(
	'clip.exe'
	'code'
	'explorer.exe'
)
for windows_binary in "${WINDOWS_BINARIES[@]}"; do
	ln -s "$(which "$windows_binary")" "$LOCAL_BIN_DIR/$windows_binary"
done

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
