SCRIPT_DIRECTORY=$(dirname "$(readlink -f "$0")")
PYTHONPATH=$SCRIPT_DIRECTORY $SCRIPT_DIRECTORY/dotfiles/__main__.py
