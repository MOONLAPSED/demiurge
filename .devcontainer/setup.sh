#!/bin/bash
# /.devcontainer/setup.sh
# Script to configure Docker and NFS in a container not to be used in production.
# NOT TO BE USED IN PRODUCTION - SAFTEY CONCERNS
set -e  # Exit on any error

echo "Setting up the Demiurge dev environment..."
# NFS Configuration
SERVER_IP="192.168.1.10"
echo "Installing NFS server..."
sudo apt-get install -y nfs-kernel-server
echo "Creating a directory for NFS share..."
sudo mkdir /shared
echo "Configuring NFS exports..."
echo "/shared $SERVER_IP(rw,sync,no_subtree_check,no_root_squash)" | sudo tee -a /etc/exports
echo "Restarting NFS server..."
sudo systemctl restart nfs-kernel-server
echo "Opening NFS ports in the firewall..."
sudo ufw allow 2049/tcp
sudo ufw allow 2049/udp
# Docker Configuration
echo "Installing Docker..."
sudo apt-get install -y docker.io
echo "Starting a Docker container with NFS volume..."
docker run -v $SERVER_IP:/shared:/cognos_container
echo "Docker and NFS configuration complete."


# Load the correct .env file based on the current branch
BRANCH=$(git rev-parse --abbrev-ref HEAD)
if [[ "$BRANCH" == "staging" ]]; then
    cp /config/staging.env .env
elif [[ "$BRANCH" == "main" ]]; then
    cp /config/production.env .env
else
    cp /config/dev.env .env
fi

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
