# Filename: .devcontainer/Dockerfile

FROM nvidia/cuda:12.3.1-devel-ubuntu22.04

ENV DEBIAN_FRONTEND=noninteractive

# --- Stage 1: Install System Dependencies as ROOT ---
# 'unzip' and 'bubblewrap' are common opam dependencies.
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
    sudo \
    clang \
    opam \
    unzip \
    bubblewrap \
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
USER $USERNAME
WORKDIR /home/$USERNAME

# --- Stage 4: Initialize OPAM and Install OCaml for the 'vscode' user ---
# opam is already installed system-wide, so we can just use it.
RUN opam init -y --disable-sandboxing && \
    opam switch create 5.1 -y && \
    # The 'eval' is crucial for the next line to find the right OCaml compiler
    eval $(opam env) && \
    opam install -y dune ocaml-lsp-server ocamlformat