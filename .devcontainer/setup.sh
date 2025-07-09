#!/bin/bash
set -e # Exit immediately if a command exits with a non-zero status.

echo "--- Running post-create setup as user: $(whoami) ---"

# --- OCaml Shell Configuration ---
# Set up the OPAM environment variables for any new shell sessions.
# This needs to be done for both bash (for scripts) and nushell.
echo "Configuring shells for OPAM..."

# Add to .bashrc for scripts or manual bash sessions
echo -e '\n# Set up OCaml environment\neval $(opam env)' >> ~/.bashrc

# Add to Nushell's env.nu
NU_CONFIG_DIR="$HOME/.config/nushell"
mkdir -p "$NU_CONFIG_DIR"
echo 'source-env (opam env --shell=nu | from nuon)' >> "$NU_CONFIG_DIR/env.nu"

# --- Python Environment Setup ---
# Create a virtual environment using uv and install packages from requirements.txt
# This makes your Python setup reproducible and ready-to-go.
echo "Setting up Python virtual environment with uv..."
uv venv .venv --python 3.13
# Use 'sync' to ensure the venv matches requirements.txt exactly.
# Create a requirements.txt file if you don't have one!
if [ -f "requirements.txt" ]; then
    uv pip sync requirements.txt -p .venv/bin/python
else
    echo "No requirements.txt found. Skipping Python package installation."
    echo "You can create one and run 'uv pip sync requirements.txt' later."
fi

echo "--- Setup complete! ---"