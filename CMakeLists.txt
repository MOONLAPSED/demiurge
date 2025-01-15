cmake_minimum_required(VERSION 3.10)
set(CMAKE_C_STANDARD 11)
project(DEMIURGE)


REPO_URL = https://github.com/MOONLAPSED/demiurge.git
REPO_DIR = .

.PHONY: all setup git-init racket-init

# Default target: setup everything
all: setup

# Install Git using pacman
setup:
        pacman -S git --noconfirm
git-init:
    git clone $(REPO_URL) $(REPO_DIR)
racket-init:
    cd $(REPO_DIR) && raco pkg new .

# Add the executable
add_executable(demiurge main.c)