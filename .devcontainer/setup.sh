#!/bin/bash

# This script is run by 'postCreateCommand' in devcontainer.json.
# It sets up the shell environments for both Bash and Nushell.

# Ensure all commands run as the 'vscode' user, not root.
# This prevents permission errors with config files.
USERNAME="vscode"
HOME_DIR="/home/$USERNAME"

echo "--- Running post-create setup as user $(whoami) ---"

# --- Section 1: Configure Bash ---
# This is a good practice as a fallback or for scripts that expect bash.
echo "Configuring Bash environment in $HOME_DIR/.bashrc..."
echo -e '\n# Set up OPAM environment\neval $(opam env)' >> "$HOME_DIR/.bashrc"

# --- Section 2: Configure Nushell (Your Default Shell) ---
# Nushell has its own configuration files. We need to create them and
# populate them with the opam environment variables.
echo "Configuring Nushell environment..."

NU_CONFIG_DIR="$HOME_DIR/.config/nushell"
NU_ENV_FILE="$NU_CONFIG_DIR/env.nu"
NU_CONFIG_FILE="$NU_CONFIG_DIR/config.nu"

# 1. Create the Nushell config directory if it doesn't exist.
mkdir -p "$NU_CONFIG_DIR"

# 2. Ask opam to generate the environment setup script for Nushell
#    and save it to its own file (`env.nu`).
echo "Generating opam environment for Nushell..."
# We need to run this as the vscode user to get the correct paths.
sudo -u $USERNAME opam env --shell=nu > "$NU_ENV_FILE"

# 3. Add a line to the main Nushell config (`config.nu`) to "source"
#    (load) the environment file we just created.
echo "Updating $NU_CONFIG_FILE to source the environment..."
echo -e "\nsource '$NU_ENV_FILE' # Load opam environment variables" >> "$NU_CONFIG_FILE"

# 4. CRITICAL: Ensure the vscode user owns all the new config files.
#    The postCreateCommand can sometimes run as root, so this prevents permission issues.
echo "Setting correct permissions for $HOME_DIR/.config..."
chown -R $USERNAME:$USERNAME "$HOME_DIR/.config"
chown $USERNAME:$USERNAME "$HOME_DIR/.bashrc"

echo "--- Shell configuration complete! ---"

# --- Section 3: Any other setup commands can go here ---
# For example, installing Python dependencies with uv:
# echo "Installing Python packages with uv..."
# uv pip install -r requirements.txt