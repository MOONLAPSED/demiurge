#!/bin/bash
set -e  # Exit on any error

echo "Setting up the Demiurge dev environment..."

# Install Python dependencies and set up the environment
uv install --extra dev

# Generate JupyterLab configuration
uv run -m jupyterlab --generate-config

# Create a Jupyter kernel for this environment
uv run -m ipykernel install --user --name=cognosis

# Init JupyterLab
uv run --with jupyter jupyter lab --ip=0.0.0.0 --port=8888 --allow-root

# Run nox to execute predefined tasks like tests and linting
uv run -m nox -s tests  # Runs the tests session defined in the noxfile.py

# Optional: Add any additional setup steps here
echo "Demiurge development environment setup is complete."
