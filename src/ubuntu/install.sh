SCRIPT_DIRECTORY=$(dirname "$(readlink -f "$0")")

sudo apt update
sudo apt install libpython3-dev
sudo apt install python3-venv

python3 -m venv .install-venv
source .install-venv/bin/activate
pip install -r requirements.txt

PYTHONPATH=$SCRIPT_DIRECTORY $SCRIPT_DIRECTORY/dotfiles/__main__.py
