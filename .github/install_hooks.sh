#!/bin/bash

HOOKS_DIR=".git/hooks"
REPO_HOOKS="./hooks"

echo "Installing Git hooks from $REPO_HOOKS..."

for hook in $REPO_HOOKS/*; do
  hook_name=$(basename $hook)
  cp "$hook" "$HOOKS_DIR/$hook_name"
  chmod +x "$HOOKS_DIR/$hook_name"
  echo "Installed $hook_name"
done

echo "All hooks installed successfully!"
