#!/usr/bin/env fish

# Lints all bash files in the project.


set PROJECT_ROOT (realpath (dirname (status --current-filename))/..)

set bash_files (find $PROJECT_ROOT -type d \( -name .git -o -name node_modules \) -prune -false -o -type f -name '*.bash')
shellcheck $bash_files
