#!/bin/bash
# If not running interactively, don't do anything
case $- in
    *i*) ;;
      *) return;;
esac
# ==========================================================
# Aliases
# ==========================================================
alias ...='../../'
alias ..='../'
# alias cr='history | grep <search_term>' # see (reverse-i-search)`' == "ctrl+r"
# gitdoc  # see (gitdoc) below
# H [] # see (H) below
# alert [] # see (alert) below
# popx [] # see (popx) below
# bp # see (bp) below
# .bp # see (bp) below
# backup [] # see (backup) below
# ct [] # see (ct) below
alias ls='ls --color=auto'
alias grep='grep --color=auto'
alias fgrep='fgrep --color=auto'
alias egrep='egrep --color=auto'
alias ip='ip --color=auto'
alias ll='ls -alF --color=auto'
alias la='ls -A --color=auto'
alias l='ls -CF --color=auto'
alias kex='kex --win -s'
# ==========================================================
# git Configurations
# ==========================================================
# Git Aliases, see .gitconfig for more info & aliases
alias gs='git status'
alias gca='git commit -a'
alias gcam='git commit -am'
alias gp='git push'
alias gup='git pull'
alias gco='git checkout'
alias gcb='git checkout -b'
alias gl='git log --graph --oneline --decorate --all'
alias gll='git log -1 --stat'
alias gclean='git clean -fdX'
alias diff='git diff --color-words'
alias dif='git diff --color --word-diff --stat'
# ----------------------------------------------------
# Git Functions
# reverse git add (takes off git add <file> from staging area)
function unstage() {
  git reset HEAD -- $1
}
# Enable fsmonitor-watchman deamon for git IPC
git config --global core.fsmonitor 'true'
# Git configuration
git config --global rerere.enabled true
# Reverse git add (takes off git add <file> from staging area)
unstage() {
    git reset HEAD -- $1
}
: <<'GIT_DOC'
    ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
    ┃                ⚡ Git Staging & Reset Cheat Sheet ⚡            ┃
    ┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┫
    ┃ Command                         ┃ Effect                       ┃
    ┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┫
    ┃ git add <file>                   ┃ Stage changes for commit    ┃
    ┃ gunadd <file>                     ┃ Unstage, keep changes      ┃
    ┃ git reset HEAD <file>             ┃ (Same as gunadd)           ┃
    ┃ git checkout -- <file>            ┃ Discard local changes      ┃
    ┃ git restore --staged <file>       ┃ Unstage, keep changes      ┃
    ┃ git restore <file>                ┃ Discard local changes      ┃
    ┃ git reset --soft HEAD~1           ┃ Undo commit, keep staged   ┃
    ┃ git reset --mixed HEAD~1          ┃ Undo commit, unstage files ┃
    ┃ git reset --hard HEAD~1           ┃ Undo commit & changes! ⚠   ┃
    ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

    🔥 `gunadd` is an alias for:
       git reset HEAD <file>    # Unstages, but keeps file changes

    ⚠  Use `git reset --hard` with caution—it nukes all changes!

GIT_DOC
alias gitdoc='cat <<EOF
# (Paste the docstring here)
EOF'
# ==========================================================
# Shell Behavior Enhancements
# ==========================================================
# Enable bash history features
HISTCONTROL=ignoreboth
HISTSIZE=5000
HISTFILESIZE=10000
shopt -s histappend checkwinsize
# Set a colored prompt
force_color_prompt=yes
if [ -n "$force_color_prompt" ]; then
    if [ -x /usr/bin/tput ] && tput setaf 1 >&/dev/null; then
        color_prompt=yes
    fi
fi

if [ "$color_prompt" = yes ]; then
    PS1='${debian_chroot:+($debian_chroot)}\[\033[01;32m\]\u@\h\[\033[00m\]:\[\033[01;34m\]\w\[\033[00m\]\$ '
else
    PS1='${debian_chroot:+($debian_chroot)}\u@\h:\w\$ '
fi
# enable programmable completion features (you don't need to enable
# this, if it's already enabled in /etc/bash.bashrc and /etc/profile
# sources /etc/bash.bashrc).
if ! shopt -oq posix; then
  if [ -f /usr/share/bash-completion/bash_completion ]; then
    . /usr/share/bash-completion/bash_completion
  elif [ -f /etc/bash_completion ]; then
    . /etc/bash_completion
  fi
fi
if [ -x /usr/bin/dircolors ]; then
    test -r ~/.dircolors && eval "$(dircolors -b ~/.dircolors)" || eval "$(dircolors -b)"
    export LS_COLORS="$LS_COLORS:ow=30;44:" # fix ls color for folders with 777 permissions
# ==========================================================
# Custom History Search Functions
# ==========================================================
# Smart command history search
cr() {
    history | grep --color=auto -i "$@"
}

# Filter command history with reverse sorting and unique results
H() {
    history | grep -i "$@" | sort -r | uniq
}




















# ==========================================================
# Colorized Output Functions
# ==========================================================
# Define basic ANSI color escape codes for named colors
RED='\033[38;5;196m'
GREEN='\033[38;5;46m'
YELLOW='\033[38;5;226m'
BLUE='\033[38;5;21m'
PURPLE='\033[38;5;93m'
NC='\033[0m' # No Color
# General-purpose function to colorize text
ct() {
    local color_code="$1"
    shift
    echo -e "${color_code}$*${NC}"
}
# NAMED color functions
red() { color_text "$RED" "$@"; }
green() { color_text "$GREEN" "$@"; }
yellow() { color_text "$YELLOW" "$@"; }
blue() { color_text "$BLUE" "$@"; }
purple() { color_text "$PURPLE" "$@"; }
# Color Picker: Cycles through all 256 available colors in the terminal
cpick() {
    for i in {0..255}; do
        # Print each color number in its respective color
        echo -en "\033[38;5;${i}m${i} \033[0m"
        # Line break after every 16 colors for readability
        if (( (i + 1) % 16 == 0 )); then
            echo # New line
        fi
    done

    # Displaying named colors at the end of the cycle
    echo -e "\nNamed Colors:"
    echo -e "${RED}RED    \033[0m"
    echo -e "${GREEN}GREEN  \033[0m"
    echo -e "${YELLOW}YELLOW \033[0m"
    echo -e "${BLUE}BLUE   \033[0m"
    echo -e "${PURPLE}PURPLE \033[0m"

}
echo "$(green "demiurge spectral #'s:.")"
cpick
# ==========================================================
# BASH and prompt Configurations
# ==========================================================
# Colored GCC warnings and errors
export GCC_COLORS='error=01;31:warning=01;35:note=01;36:caret=01;32:locus=01:quote=01'
force_color_prompt=yes
if [ -n "$force_color_prompt" ]; then
    if [ -x /usr/bin/tput ] && tput setaf 1 >&/dev/null; then
        # We have color support; assume it's compliant with Ecma-48
        # (ISO/IEC-6429). (Lack of such support is extremely rare, and such
        # a case would tend to support setf rather than setaf.)
        color_prompt=yes
    else
        color_prompt=
    fi
fi
if [ "$color_prompt" = yes ]; then
    PS1='${debian_chroot:+($debian_chroot)}\[\033[01;32m\]\u@\h\[\033[00m\]:\[\033[01;34m\]\w\[\033[00m\]\$ '
else
    PS1='${debian_chroot:+($debian_chroot)}\u@\h:\w\$ '
fi
# Set a colored prompt
force_color_prompt=yes
if [ -n "$force_color_prompt" ]; then
    if [ -x /usr/bin/tput ] && tput setaf 1 >&/dev/null; then
        color_prompt=yes
    fi
fi

if [ "$color_prompt" = yes ]; then
    PS1='${debian_chroot:+($debian_chroot)}\[\033[01;32m\]\u@\h\[\033[00m\]:\[\033[01;34m\]\w\[\033[00m\]\$ '
else
    PS1='${debian_chroot:+($debian_chroot)}\u@\h:\w\$ '
fi
# Check if the shell is running interactively
check_interactive_shell() {
    case "$-" in
        *i*) return 0 ;; # Interactive shell
        *) return 1 ;;   # Non-interactive shell
    esac
}
# Set variable identifying the chroot (if available)
if [ -z "${debian_chroot:-}" ] && [ -r /etc/debian_chroot ]; then
    debian_chroot=$(cat /etc/debian_chroot)
fi
# Function to set up terminal title and color support
setup_terminal() {
    case "$TERM" in
        xterm*|rxvt*)
            PS1="\[\e]0;${debian_chroot:+($debian_chroot)}\u@\h: \w\a\]$PS1"
            ;;
        *)
            ;;
    esac
    # Enable color support of ls and also add handy aliases
    if [ -x /usr/bin/dircolors ]; then
        test -r ~/.dircolors && eval "$(dircolors -b ~/.dircolors)" || eval "$(dircolors -b)"
        alias ls='ls --color=auto'
        alias grep='grep --color=auto'
        alias fgrep='fgrep --color=auto'
        alias egrep='egrep --color=auto'
        alias lll='ls -lka --color=auto'
        alias ll='ls -alF --color=auto'
        alias la='ls -A --color=auto'
        alias l='ls -CF --color=auto'
    fi
    # Colored GCC warnings and errors
    export GCC_COLORS
}
# Check if terminal setup should be enabled
if [ -n "$ENABLE_TERMINAL_SETUP" ]; then
    setup_terminal

# ==========================================================
# Custom Functions
# ==========================================================
# cr - Reverse search through command history
#
# Usage:
#   cr [PATTERN]
#
# This function allows you to search through your command history in reverse order.
# If no PATTERN is provided, it will search for the last executed command.
# If PATTERN is provided, it will search for commands containing that pattern.
#
# The search results are displayed with line numbers, and you can enter the line
# number to re-execute the corresponding command.
#
# Examples:
#   cr         # Search for the last executed command
#   cr apt     # Search for commands containing the pattern "apt"
#   cr 'apt install'  # Search for commands containing the exact phrase "apt install"
#
cr() {
  if [ $# -eq 0 ]; then
    last_cmd="$(fc -ln -1 | sed "s/^\s*//")"
    if [ -n "$last_cmd" ]; then
      HISTTIMEFORMAT= histunique | grep -i "$last_cmd"
    fi
  else
    HISTTIMEFORMAT= histunique | grep -i "$@"
  fi
  echo -ne "\033[32m(reverse-i-search)\033[0m"': '
}
# ----------------------------------------------------	
# H - Custom command history filtering
#
# Usage:
#   H [PATTERN]
#
# This function filters and sorts the command history based on the provided PATTERN.
# It removes duplicate commands and sorts the output in reverse chronological order.
#
# The function performs the following steps:
#   1. Excludes lines that represent invocations of the `H` function itself.
#   2. Filters the remaining lines based on the provided PATTERN.
#   3. Sorts the output in reverse order based on the second column (command timestamp).
#   4. Removes duplicate lines, considering all fields except the first (line number).
#   5. Performs a final sorting of the output.
#
# If no PATTERN is provided, it will display the entire command history.
#
# Examples:
#   H             # Show the entire command history
#   H apt         # Show commands containing the pattern "apt"
#   H 'apt install'  # Show commands containing the exact phrase "apt install"
#
H() {
    history | egrep -v '^ *[[:digit:]]+ +H +' | grep "$@" | sort -rk 2 | uniq -f 1 | sort
}
# ----------------------------------------------------
# backup - Create a backup copy of a file
#
# Usage:
#   backup FILENAME
#
# This function creates a backup copy of the specified file with the ".bak" extension.
#
# Arguments:
#   FILENAME - The name of the file to be backed up.
#
# Example:
#   backup important_file.txt
#
# This will create a backup copy named "important_file.txt.bak" in the same directory.
#
function backup() {
    cp "$1" "$1.bak"
}

# alert - Notify when a long-running command completes
#
# Usage:
#   command; alert
#
# This alias is used to notify the user when a long-running command completes.
# It prints the last executed command with the prefix "Command completed: ".
#
# To use it, simply append `; alert` to the end of the command you want to monitor.
#
# Example:
#   sleep 10; alert
#
# This will execute the `sleep 10` command and print "Command completed: sleep 10" when it finishes.
#
alias alert='echo "Command completed: $(history|tail -n1|sed -e '\''s/^\s*[0-9]\+\s*//;s/[;&|]\s*alert$//'\'')"'
# ----------------------------------------------------
# popx - Pop multiple directories from the directory stack
#
# Usage:
#   popx NUM
#
# This function pops NUM directories from the directory stack and prints the current
# working directory after the operation.
#
# Arguments:
#   NUM - The number of directories to pop from the stack (must be > 0).
#
# If the directory stack is empty or if NUM is less than or equal to 0,
# an error message is displayed, and the function returns with an error code.
#
# Example:
#   popx 3
#
# This will pop the last 3 directories from the stack and print the current
# working directory after the operation.
#
popx() {
  if [ $# -ne 1 ]; then
    echo "Usage: popx <num>"
    return 1
  fi
  num=$1
  if [ $num -le 0 ]; then
    echo "Error: Number must be > 0"
    return 1
  fi
  for ((i=0; i<num; i++)); do
    if [ ${#DIR_STACK[@]} -eq 0 ]; then
      echo "Error: Directory stack empty"
      return 1
    fi
    popd > /dev/null || break
  done
  pwd
}
# ----------------------------------------------------------
# bp - Backport non-hidden files and directories to parent directory
#
# Usage:
#   bp
#
# This function copies all non-hidden files and directories from the current
# directory to the parent directory.
#
# Example:
#   bp
#
bp() {
    cp -r ./* ../
}

# .bp - Backport all files and directories to parent directory
#
# Usage:
#   .bp
#
# This function copies all files and directories (including hidden ones) from the
# current directory to the parent directory.
#
# After copying the files and directories, it prompts the user to confirm whether
# to delete the current directory if it's empty. If the user confirms, it deletes
# the current directory and changes to the parent directory.
#
# Example:
#   .bp
#
.bp() {
    local current_dir="$(pwd)"
    local parent_dir="$(dirname "$current_dir")"

    # Check if the current directory is not the root directory
    if [[ "$current_dir" == "/" ]]; then
        echo "Cannot move the root directory."
        return 1
    fi

    # Copy all files and directories (including hidden ones)
    shopt -s dotglob # Enable matching dotfiles
    for item in ./*; do
        if [[ -e "$item" ]]; then
            cp -rv --no-preserve=mode "$item" "$parent_dir" || return
            rm -rf "$item"
        fi
    done
    shopt -u dotglob # Disable matching dotfiles

    # Change to the parent directory
    cd "$parent_dir" || return

    echo "All files and directories copied and deleted from the current directory."
}
# ==========================================================
# External Packages
# ==========================================================
# >>> conda initialize >>>
# !! Contents within this block are managed by 'conda init' !!
__conda_setup="$('/home/tp/miniconda/bin/conda' 'shell.bash' 'hook' 2> /dev/null)"
if [ $? -eq 0 ]; then
    eval "$__conda_setup"
else
    if [ -f "/home/tp/miniconda/etc/profile.d/conda.sh" ]; then
        . "/home/tp/miniconda/etc/profile.d/conda.sh"
    else
        export PATH="/home/tp/miniconda/bin:$PATH"
    fi
fi
unset __conda_setup
# <<< conda initialize <<<