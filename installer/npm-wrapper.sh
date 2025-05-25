#!/bin/bash
# Wrapper script to ensure node is in PATH for npm commands

# Add nvm node to PATH
NVM_DIRS=("$HOME/.nvm" "$HOME/.local/share/nvm")

for nvm_dir in "${NVM_DIRS[@]}"; do
    if [ -d "$nvm_dir/v22.16.0" ]; then
        export PATH="$nvm_dir/v22.16.0/bin:$PATH"
        break
    fi
done

# Execute npm with all arguments
exec npm "$@"