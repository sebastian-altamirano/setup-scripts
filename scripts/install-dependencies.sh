#!/usr/bin/env sh

SCRIPT_PATH=$(readlink -f "$0")
WORKSPACE_ROOT=$(dirname "$(dirname "$SCRIPT_PATH")")

cd $WORKSPACE_ROOT
npm install

cd "$WORKSPACE_ROOT/src/ubuntu"
pdm install
