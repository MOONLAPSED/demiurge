# Filename: .devcontainer/Dockerfile

FROM nvidia/cuda:12.3.1-devel-ubuntu22.04

ENV DEBIAN_FRONTEND=noninteractive

# --- Stage 1: Install System Dependencies as ROOT ---
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

# --- Stage 4: Set Build-Time Environment Variables for OPAM ---
# This controls the opam build process in the RUN commands below.
# Using OPAMJOBS=1 is crucial for low-resource environments.
ENV OPAMYES=1
ENV OPAMJOBS=1
ENV OPAMSWITCH=5.3.0
ENV PATH="/home/vscode/.opam/${OPAMSWITCH}/bin:$PATH"

# --- Stage 5: Initialize OPAM and Create Switch ---
RUN opam init --disable-sandboxing --reinit -y && \
    opam switch create $OPAMSWITCH -y

# --- Stage 6: Install OCaml Tools Incrementally to Manage Disk Space ---
# Install dune and ocamlformat first, then clean up their build files.
RUN opam install -y dune ocamlformat && \
    opam clean -a -c -s --logs

# Now, install the largest package, ocaml-lsp-server, by itself and clean again.
RUN opam install -y ocaml-lsp-server && \
    opam clean -a -c -s --logs

# --- Stage 7: Final User Configuration ---
# This configures the interactive shells for when the container is running.
RUN echo '\n# Set up OCaml environment\neval $(opam env)' >> /home/vscode/.bashrc && \
    mkdir -p /home/vscode/.config/dune && \
    echo "(j 1)" > /home/vscode/.config/dune/config && \
    mkdir -p /home/vscode/.config/nushell && \
    echo 'source-env (opam env --shell=nu | from nuon)' >> /home/vscode/.config/nushell/env.nu