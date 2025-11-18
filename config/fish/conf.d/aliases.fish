abbr -a - 'cd -'
abbr -a c clear

abbr -a e explorer.exe
abbr -a g git

abbr -a --position anywhere -- --help '--help | bat -plhelp'

alias .. 'cd ..'
alias ... 'cd ../..'
alias .... 'cd ../../..'

alias bat batcat

alias hs 'history | grep'

alias ls 'eza --group-directories-first --icons --oneline'
alias la 'eza --group-directories-first --icons --all --oneline'
alias ll 'eza --group-directories-first --icons --all --long --git'

alias upd 'sudo apt update && sudo apt upgrade && sudo apt autoremove'
