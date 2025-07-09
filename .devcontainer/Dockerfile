# Filename: .devcontainer/Dockerfile

# Start from the official NVIDIA base image.
# This provides Ubuntu 22.04 and the full CUDA toolkit.
FROM nvidia/cuda:12.3.1-devel-ubuntu22.04

# Set a non-interactive frontend to avoid prompts during build.
ENV DEBIAN_FRONTEND=noninteractive

# --- Stage 1: Install System Dependencies as ROOT ---
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
    sudo \
    clang \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# --- Stage 2: Create the non-root 'vscode' user as ROOT ---
ARG USERNAME=vscode
ARG USER_UID=1000
ARG USER_GID=$USER_UID
RUN groupadd --gid $USER_GID $USERNAME && \
    useradd --uid $USER_UID --gid $USER_GID -m $USERNAME --shell /bin/bash && \
    echo $USERNAME ALL=\(root\) NOPASSWD:ALL > /etc/sudoers.d/$USERNAME && \
    chmod 0440 /etc/sudoers.d/$USERNAME

# --- Stage 3: Switch to the 'vscode' user ---
# All subsequent commands will be run as this non-root user.
USER $USERNAME
WORKDIR /home/$USERNAME

# --- Stage 4: Install OCaml and OPAM as the 'vscode' user ---
# This guarantees the user exists before opam is installed.
RUN bash -c "sh <(curl -fsSL https://raw.githubusercontent.com/ocaml/opam/master/shell/install.sh)"
# We need to set the PATH here so the next RUN command can find opam
ENV PATH="/home/vscode/.opam/default/bin:${PATH}"
RUN opam init -y --disable-sandboxing && \
    opam switch create 5.1 -y && \
    eval $(opam env) && \
    opam install -y dune ocaml-lsp-server ocamlformat
