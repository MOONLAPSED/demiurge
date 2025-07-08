#!/bin/bash
set -e

echo "--- Starting post-creation setup ---"

# Ensure we're using the correct Python from the feature
PYTHON_PATH="/usr/local/bin/python"
if [ ! -f "$PYTHON_PATH" ]; then
    echo "Warning: Python not found at expected path, searching..."
    PYTHON_PATH=$(which python3)
fi

# Create Python virtual environment with uv
echo "Creating Python virtual environment..."
uv venv .venv --python "$PYTHON_PATH"

# Install Python packages
echo "Installing Python packages..."
.venv/bin/pip install -U jupyterlab nox mypy

# Verify OCaml installation and environment
echo "Verifying OCaml installation..."
if command -v opam >/dev/null 2>&1; then
    echo "OPAM found, initializing environment..."
    
    # Initialize OPAM environment if not already done
    if [ ! -d ~/.opam ]; then
        opam init -y --disable-sandboxing
    fi
    
    # Ensure correct switch is active
    opam switch 5.1.1 2>/dev/null || opam switch create 5.1.1
    
    # Install required OCaml packages if not already installed
    eval $(opam env --switch=5.1.1)
    opam install -y dune ocaml-lsp-server ocamlformat
    
    # Add OPAM environment initialization to bashrc
    echo -e '\n# Initialize OPAM environment\neval $(opam env --switch=5.1.1)' >> ~/.bashrc
    
    echo "OCaml environment setup complete"
else
    echo "Warning: OPAM not found. OCaml features may not work correctly."
fi

# Set up git configuration (optional)
echo "Setting up git configuration..."
git config --global init.defaultBranch main

# Create a simple test to verify everything works
echo "Running verification tests..."

# Test Python
echo "Testing Python installation..."
.venv/bin/python --version

# Test OCaml if available
if command -v ocaml >/dev/null 2>&1; then
    echo "Testing OCaml installation..."
    eval $(opam env --switch=5.1.1)
    ocaml -version
    
    # Test OCaml LSP
    if command -v ocamllsp >/dev/null 2>&1; then
        echo "OCaml LSP server available"
    else
        echo "Warning: OCaml LSP server not found"
    fi
fi

echo "--- Post-creation setup complete ---"
echo "Virtual environment created at: $(pwd)/.venv"
echo "To activate: source .venv/bin/activate"