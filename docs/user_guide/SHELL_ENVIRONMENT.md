# Thinkube Shell Environment

This guide explains the shell environment and utilities available across the Thinkube platform.

## Overview

Thinkube provides a consistent, feature-rich shell environment across all hosts (both physical servers and virtual machines) with:

- **Custom Starship prompt** with a theme inspired by Tokyo Night color scheme
- **Common functions** shared across Bash, Zsh and Fish
- **Dynamic aliases/abbreviations** appropriate for each shell
- **Documentation** accessible directly from the command line

The shell environment is designed to prevent recursive loading issues while providing a consistent experience across different shell types. Each shell (Bash, Zsh, and Fish) has customized configurations that maintain feature parity while respecting shell-specific idioms and best practices.

## Getting Started

After logging into any Thinkube host, your shell is already configured with these features. Here are a few helpful commands to get started:

```bash
# List all available functions
list_functions

# List all available functions with descriptions
list_functions -d

# Show documentation for functions
show_function_docs

# List all aliases/abbreviations
aliases
```

## Shell Features

### Starship Prompt

The Thinkube shell environment uses [Starship](https://starship.rs/) with a custom theme inspired by the Tokyo Night color palette. The prompt provides:

- Current shell indicator (Bash/Zsh/Fish)
- Current directory with intelligent truncation
- Git branch and status when in a Git repository
- Language version indicators (Node.js, Python, Rust, Go)
- Current time
- Exit status of the last command

### Shared Functions

Functions work identically across all shell environments (Bash, Zsh, and Fish). Key utilities include:

| Function | Description |
|----------|-------------|
| `load_dotenv [path]` | Load environment variables from a .env file |
| `mkcd <dir>` | Create a directory and change to it in one command |
| `extract <file>` | Extract any archive format automatically |
| `sysinfo` | Display system information (hostname, kernel, memory, disk) |
| `fif <pattern> [dir]` | Find text in files (recursive grep) |
| `list_functions` | List all available functions |
| `create_function <name>` | Create a new custom function |
| `reload_functions` | Reload function definitions in current shell |

### Git Shortcuts

Git operations are streamlined with these shortcuts:

| Function | Description |
|----------|-------------|
| `g` | Shortcut for `git` |
| `gst` | Git status |
| `gpl` | Git pull |
| `gd` | Git diff |
| `gb` | Git branch |
| `gco` | Git checkout |
| `gcm "message"` | Git commit with message |
| `gsh` | Git stash |
| `git_shortcuts` | List all available Git shortcuts |

### Common Aliases

These aliases are available in all shells:

| Alias | Command | Description |
|-------|---------|-------------|
| `ll` | `ls -la` | List files with details |
| `la` | `ls -A` | List all files |
| `l` | `ls -CF` | List files in columns |
| `..` | `cd ..` | Go up one directory |
| `...` | `cd ../..` | Go up two directories |
| `k` | `kubectl` | Shortcut for kubectl |
| `mk` | `microk8s kubectl` | Shortcut for microk8s kubectl |
| `ans` | `ansible` | Shortcut for ansible |
| `ansp` | `ansible-playbook` | Shortcut for ansible-playbook |
| `ansl` | `ansible-lint` | Shortcut for ansible-lint |
| `tf` | `terraform` | Shortcut for terraform |
| `dk` | `docker` | Shortcut for docker |
| `runplay` | `~/thinkube/scripts/run_ansible.sh` | Run ansible playbook |

### Fish Shell Enhancements

When using Fish shell, all aliases are implemented as **abbreviations**, which provide these benefits:

- Display the full command before execution
- Allow editing before running
- Support dynamic expansion with placeholder substitution
- Can be used anywhere in command line, not just at the beginning

The following Fish plugins are also installed:

- `fzf.fish` - Fuzzy search history, files, and directories
- `bass` - Run Bash utilities in Fish
- `done` - Notification when long-running commands complete
- `autopair` - Auto-close parentheses, quotes, etc.

### Cross-Shell Aliases Implementation

The shell environment implements a unified alias system that works across different shells:

- **For Bash/Zsh**: Traditional aliases are created using the `alias` command
- **For Fish**: Abbreviations are created using the `abbr` command

This is implemented through a common aliases source (`.sh` files) that are processed differently for each shell:

1. **Bash/Zsh Processing**: 
   - Direct sourcing of alias definitions which use the `alias` command
   - Example: `alias ll='ls -la'` defined in a `.sh` file

2. **Fish Processing**:
   - A converter function reads `.sh` alias files and extracts alias definitions
   - Converts each Bash/Zsh alias into a Fish abbreviation
   - Example: `alias ll='ls -la'` becomes `abbr -a ll 'ls -la'`

This approach maintains a single source of truth for aliases while adapting to each shell's preferred implementation.

## Customization

### Adding Custom Functions

Create your own functions that will work across all shells:

```bash
# Create a new function (will prompt for details)
create_function my_function "Description of what my function does" --edit

# Force reload to make it available immediately
reload_functions
```

Functions are stored in `~/.user_shared_shell/functions/` as individual files.

### Adding Custom Aliases

You can add custom aliases or abbreviations by creating files in:

- **Bash/Zsh aliases**: Create `.sh` files in `~/.user_shared_shell/aliases/`
- **Fish abbreviations**: Create `.fish` files in `~/.user_shared_shell/aliases/`

Example for Bash/Zsh (`~/.user_shared_shell/aliases/my_aliases.sh`):

```bash
# My custom aliases
alias cls='clear'
alias pyserver='python -m http.server'
```

Example for Fish (`~/.user_shared_shell/aliases/my_aliases.fish`):

```fish
# My custom abbreviations
abbr -a cls 'clear'
abbr -a pyserver 'python -m http.server'
```

After adding these files, run `load_aliases -r` to refresh the aliases.

## Environment Variables

The Thinkube shell environment automatically loads environment variables from `~/.env` if it exists. This allows you to set environment-specific variables without modifying shell configuration files.

For example, to set Ansible credentials:

```bash
# Add to ~/.env
echo 'ANSIBLE_BECOME_PASSWORD=mypassword' >> ~/.env
```

## Directory Structure

The shell configuration uses these directories:

- **System directories**:
  - `~/.thinkube_shared_shell/` - Base system directory
  - `~/.thinkube_shared_shell/functions/` - Shared system functions
  - `~/.thinkube_shared_shell/aliases/` - Shared system aliases
  - `~/.thinkube_shared_shell/docs/` - System documentation
  - `~/.thinkube_shared_shell/system/` - System scripts and configuration

- **User directories**:
  - `~/.user_shared_shell/` - Base user directory
  - `~/.user_shared_shell/functions/` - User-defined functions
  - `~/.user_shared_shell/aliases/` - User-defined aliases

### Files Structure

Key files in the shell environment:

- **Loader scripts**:
  - `~/.thinkube_shared_shell/system/load_functions.sh` - Load functions in Bash/Zsh
  - `~/.thinkube_shared_shell/system/load_functions.fish` - Load functions in Fish
  - `~/.thinkube_shared_shell/functions/load_aliases.sh` - Load aliases in Bash/Zsh
  - `~/.thinkube_shared_shell/functions/load_aliases.fish` - Load aliases in Fish

- **Shell config files**:
  - `~/.bashrc` - Bash configuration
  - `~/.zshrc` - Zsh configuration
  - `~/.config/fish/config.fish` - Fish configuration

- **Starship configuration**:
  - `~/.config/starship.toml` - Starship prompt configuration

## Troubleshooting

If you encounter issues with the shell environment, try these steps:

1. **Reload functions**: `reload_functions`
2. **Regenerate aliases**: `load_aliases -r`
3. **Check Starship installation**: `which starship`
4. **Verify configuration files**:
   - Bash: `~/.bashrc`
   - Zsh: `~/.zshrc`
   - Fish: `~/.config/fish/config.fish`

### Common Issues and Solutions

#### Shell Entering Infinite Loop

If your shell seems to hang or shows repeated messages:

- **Cause**: Recursive loading of function or alias files without proper guards, or multiple sources loading aliases
- **Solution**: 
  - Ensure all loader scripts have proper recursive loading guards
  - For Fish shell, ensure aliases are loaded ONLY via functions loader, not separately in config.fish
- **Temporary Fix**: Exit and restart the shell, or run these commands:
  - Fish: `set -e __THINKUBE_FUNCTIONS_LOADED __THINKUBE_ALIASES_LOADED`
  - Bash/Zsh: `unset __THINKUBE_FUNCTIONS_LOADED __THINKUBE_ALIASES_LOADED`

#### Starship Prompt Not Showing

If the Starship prompt isn't appearing:

- **Cause**: Improper initialization in shell config files or Starship not installed
- **Solution**:
  - Verify installation: `which starship`
  - Check initialization in appropriate shell config:
    - Bash: `starship init bash | source`
    - Zsh: `eval "$(starship init zsh)"`
    - Fish: `starship init fish | source`
  - Ensure initialization happens before loading other configurations

#### Fish Abbreviations Not Working

If Fish abbreviations aren't expanding:

- **Cause**: Alias loader not running or Fish abbreviations not created correctly
- **Solution**:
  - Reload aliases: `source ~/.thinkube_shared_shell/functions/load_aliases.fish`
  - Check if abbreviations exist: `abbr -l`
  - Verify Fish version is 3.1.0 or later: `fish --version`

#### Generate Abbreviations Process Infinite Loop

If you notice high memory usage and thousands of fish processes running:

- **Cause**: The generate_abbreviations.fish script can enter a recursive loop
- **Symptoms**:
  - High memory usage that increases over time
  - System becomes unresponsive
  - `ps aux | grep fish` shows thousands of fish processes
  - "Regenerating shared abbreviations..." message repeating endlessly
- **Solution**:
  - Kill all fish processes: `pkill -f 'fish'`
  - Reset shell configs: 
    ```bash
    mv ~/.bashrc ~/.bashrc.bak && cp /etc/skel/.bashrc ~/.bashrc
    mv ~/.zshrc ~/.zshrc.bak 2>/dev/null || true
    mv ~/.config/fish/config.fish ~/.config/fish/config.fish.bak 2>/dev/null || true
    ```
  - Reboot the system: `sudo reboot`
  - After reboot, run the shell setup playbook again with fixed code that includes proper recursive loading prevention

## Implementation Details

The Thinkube shell environment is managed through several Ansible playbooks:

1. **00_setup_shells.yml** - Core shell environment (baremetal and container hosts):
   - Shared functions loader system
   - Aliases/abbreviations generator system
   - Custom Starship prompt with colors inspired by Tokyo Night palette
   - Fish plugins and enhancements

2. **10_install_nerd_fonts.yml** - Developer fonts (desktop hosts only):
   - Installs programming-optimized fonts with icons and ligatures
   - Configures fonts for terminal, VS Code, and text editors
   - Sets up Nerd Font support for terminal icons

3. **30_setup_dev_tools.yml** - Development tools (baremetal and container hosts):
   - Installs programming languages (Go, Rust)
   - Configures development environments
   - Sets up language version managers and tools

4. **50_setup_tmux.yml** - Terminal multiplexer (baremetal and container hosts):
   - Configures tmux with sensible defaults
   - Sets up clipboard integration
   - Creates helpful aliases for tmux management

5. **60_setup_ptyxis.yml** - GNOME terminal (desktop hosts only):
   - Installs modern GNOME terminal app via Flatpak
   - Configures with tmux integration
   - Sets up profiles and color schemes

6. **70_setup_claude.yaml** - Claude Code CLI (bcn1 host only):
   - Installs Node.js and NPM
   - Sets up Claude Code global installation
   - Configures OAuth authentication process

### Shell Environment Structure

The 00_setup_shells.yml playbook is organized into modular task files:

- **00_core_shell_setup.yml** - Basic shell configuration
- **01_starship_setup.yml** - Starship prompt installation and configuration
- **02_functions_system.yml** - Shared functions system setup
- **03_aliases_system.yml** - Aliases and abbreviations system
- **04_fish_plugins.yml** - Fish-specific plugins and enhancements
- **05_shell_config.yml** - Shell-specific configurations

### Loading Mechanism and Recursive Protection

To prevent recursive loading issues, the shell environment implements guards in key files and coordinates loading between the function loader and alias loader:

#### Bash/Zsh
```bash
# Guard against recursive loading in load_functions.sh
if [ -n "$__THINKUBE_FUNCTIONS_LOADED" ]; then
  return 0
fi
__THINKUBE_FUNCTIONS_LOADED=1

# Guard against recursive loading in load_aliases.sh
if [ -n "$__THINKUBE_ALIASES_LOADED" ]; then
  return 0
fi
__THINKUBE_ALIASES_LOADED=1
```

#### Fish
```fish
# Guard against recursive loading in load_functions.fish
if set -q __THINKUBE_FUNCTIONS_LOADED
    return 0
end
set -g __THINKUBE_FUNCTIONS_LOADED 1

# Guard against recursive loading in load_aliases.fish
if set -q __THINKUBE_ALIASES_LOADED
    return 0
end
set -g __THINKUBE_ALIASES_LOADED 1

# Coordinated loading between functions and aliases loaders
# In load_functions.fish:
if test -f "$ALIASES_LOADER_FILE" -a -z "$__THINKUBE_ALIASES_LOADED"
    source "$ALIASES_LOADER_FILE"
end
```

These guards ensure that even if a script sources another script that attempts to load functions or aliases again, the recursive loading will be prevented. The Fish shell implementation also uses a coordinated loading approach where:

1. Only the functions loader is directly sourced in `config.fish`
2. The functions loader then loads the aliases loader if it hasn't been loaded yet
3. Each loader checks its respective guard variable to prevent recursive loading

### Shell Initialization Sequence

The shell initialization sequence is carefully ordered to ensure proper functionality:

1. **Shell startup file is read** (`.bashrc`, `.zshrc`, or `config.fish`)
2. **Starship prompt is initialized** first to ensure it's available
3. **Functions are loaded** from system and user directories
4. **Aliases are loaded** from system and user directories (directly in Bash/Zsh, via the functions loader in Fish)

This sequence ensures that:
- The Starship prompt is available throughout the shell session
- Functions are available for use by aliases
- All customizations are properly loaded before the shell becomes interactive

#### Initialization Example (Bash)

```bash
# ~/.bashrc

# ... (other Bash configuration)

# Initialize Starship prompt
eval "$(starship init bash)"

# Load Thinkube shared functions
if [ -f "$HOME/.thinkube_shared_shell/system/load_functions.sh" ]; then
    source "$HOME/.thinkube_shared_shell/system/load_functions.sh"
fi

# Load shared aliases
if [ -f "$HOME/.thinkube_shared_shell/functions/load_aliases.sh" ]; then
    source "$HOME/.thinkube_shared_shell/functions/load_aliases.sh"
fi
```

#### Initialization Example (Fish)

```fish
# ~/.config/fish/config.fish

# ... (other Fish configuration)

# Initialize Starship prompt
if command -v starship >/dev/null 2>&1
    starship init fish | source
end

# Load Thinkube shared functions (which will also load aliases)
if test -f "$HOME/.thinkube_shared_shell/load_functions.fish"
    source "$HOME/.thinkube_shared_shell/load_functions.fish"
end

# NOTE: Aliases are now loaded by the functions loader
# Do not load aliases separately to avoid recursive loading
```