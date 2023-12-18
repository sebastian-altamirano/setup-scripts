#!/usr/bin/env fish

# $argv[1]: SSH private key path.

eval $(ssh-agent -c)
ssh-add $argv[1]
