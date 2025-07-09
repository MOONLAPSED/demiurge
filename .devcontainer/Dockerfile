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

# --- Stage 4: Install OCaml and OPAM as the 'vscode' user ---
# We tell it WHERE to install opam, so it doesn't have to ask.
RUN bash -c "sh <(curl -fsSL https://raw.githubusercontent.com/ocaml/opam/master/shell/install.sh) --prefix /home/vscode/.local --bin /home/vscode/.local/bin"

# We need to set the PATH here so the next RUN command can find opam
ENV PATH="/home/vscode/.local/bin:${PATH}"

# Now, initialize opam and install packages. The `eval $(opam env)` makes sure
# the OCaml compiler and tools are on the path for the `opam install` command.
RUN opam init -y --disable-sandboxing && \
    opam switch create 5.1 -y && \
    eval $(opam env) && \
    opam install -y dune ocaml-lsp-server ocamlformat