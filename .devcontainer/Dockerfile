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
# We do all opam work in one layer and then clean up to save space.
RUN opam init -y --disable-sandboxing && \
    opam switch create 5.3.0 -y && \
    echo 'eval $(opam env)' >> /home/vscode/.bashrc && \
    # The 'eval' is crucial to make the next command aware of the new switch
    eval $(opam env) && \
    opam install -y dune ocaml-lsp-server ocamlformat && \
    # Clean up build artifacts to reduce layer size
    opam clean && \
    rm -rf /home/vscode/.opam/5.3.0/.opam-switch/build/*

# --- Stage 5: Configure Shells ---
# This ensures that when you open a terminal, the opam environment is active.
RUN echo '\n# Set up OCaml environment\neval $(opam env)' >> /home/vscode/.bashrc && \
    mkdir -p /home/vscode/.config/nushell && \
    echo 'source-env (opam env --shell=nu | from nuon)' >> /home/vscode/.config/nushell/env.nu

# Add environment variables
ENV OPAMYES=true
ENV OPAMJOBS=1
ENV PATH="/home/vscode/.opam/default/bin:$PATH"
# RUN echo 'eval $(opam env)' >> /home/vscode/.bashrc
# Create dune config to limit build jobs
RUN mkdir -p /home/vscode/.config/dune && \
    echo "(j 1)" > /home/vscode/.config/dune/config
    chown -R vscode:vscode /home/vscode/.config
    