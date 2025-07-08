FROM nvidia/cuda:12.3.1-devel-ubuntu22.04
# --- Pre-build
# This ARG receives the value from devcontainer.json's "build.args"
ARG INSTALL_CUDA="false"

# Set a non-interactive frontend to avoid prompts during build
ENV DEBIAN_FRONTEND=noninteractive

# Basic setup: install sudo, git, curl, etc.
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
    sudo \
    ca-certificates \
    clang lldb \
    && rm -rf /var/lib/apt/lists/*

# If using devcontainers, omit the following which is done automatically:
# Create a non-root user that matches your local user.
# This improves security and fixes potential file permission issues.
# VS Code will automatically use this user.
# ARG USERNAME=vscode
# ARG USER_UID=1000
# ARG USER_GID=$USER_UID
# RUN groupadd --gid $USER_GID $USERNAME && \
#     useradd --uid $USER_UID --gid $USER_GID -m $USERNAME && \
#     echo $USERNAME ALL=\(root\) NOPASSWD:ALL > /etc/sudoers.d/$USERNAME && \
#     chmod 0440 /etc/sudoers.d/$USERNAME
