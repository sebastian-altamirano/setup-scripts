#!/usr/bin/env fish

# Formats all fish shell files in the project.


set PROJECT_ROOT (realpath (dirname (status --current-filename))/..)

set fish_files (find $PROJECT_ROOT -type d \( -name .git -o -name node_modules \) -prune -false -o -type f -name '*.fish')
fish_indent -w $fish_files
