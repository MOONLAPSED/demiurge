#!/bin/bash
set -e # Exit immediately if a command exits with a non-zero status.

echo "--- Starting post-creation setup ---"

# If you have provisioning steps, run them here.
# Assuming provisioning.sh is for local use and not Codespaces based on your onCreateCommand.
if [ ! "$CODESPACES" = "true" ]; then
    echo "Running provisioning.sh for non-Codespaces environment..."
    bash .devcontainer/provisioning.sh
fi

echo "Copying .bashrc..."
cp .devcontainer/.bashrc ~/.bashrc

echo "Creating Python virtual environment with uv..."
# The 'uv' feature should have already added it to the PATH
uv venv .venv

echo "Installing Python packages into .venv..."
# Activate the venv and install packages in a subshell
# Or, more robustly, call the python/pip from within the venv directly
.venv/bin/pip install -U jupyterlab nox

echo "--- Post-creation setup complete ---"