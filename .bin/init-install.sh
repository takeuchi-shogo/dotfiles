#!/bin/bash
# =============================================================================
# Dotfiles Initial Setup Script
# =============================================================================

DOTFILES_DIR="$HOME/dotfiles"
LOG_FILE="/tmp/dotfiles-install-$(date +%Y%m%d-%H%M%S).log"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# =============================================================================
# Helper Functions
# =============================================================================
log() {
  echo -e "${GREEN}[INFO]${NC} $1"
  echo "[INFO] $1" >> "$LOG_FILE"
}

warn() {
  echo -e "${YELLOW}[WARN]${NC} $1"
  echo "[WARN] $1" >> "$LOG_FILE"
}

error() {
  echo -e "${RED}[ERROR]${NC} $1"
  echo "[ERROR] $1" >> "$LOG_FILE"
  exit 1
}

section() {
  echo ""
  echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
  echo -e "${BLUE}  $1${NC}"
  echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
  echo ""
}

command_exists() {
  command -v "$1" &> /dev/null
}

# =============================================================================
# Xcode Command Line Tools
# =============================================================================
install_xcode_cli() {
  section "Xcode Command Line Tools"

  if xcode-select -p &> /dev/null; then
    log "Xcode Command Line Tools is already installed"
  else
    log "Installing Xcode Command Line Tools..."
    xcode-select --install

    # Wait for installation to complete
    echo "Waiting for Xcode CLI installation..."
    echo "Press any key after installation is complete..."
    read -n 1 -s
  fi
}

# =============================================================================
# Homebrew
# =============================================================================
install_homebrew() {
  section "Homebrew"

  if command_exists brew; then
    log "Homebrew is already installed"
    log "Updating Homebrew..."
    brew update || warn "Failed to update Homebrew"
  else
    log "Installing Homebrew..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

    # Add to PATH for Apple Silicon
    if [[ $(uname -m) == "arm64" ]]; then
      local brew_env='eval "$(/opt/homebrew/bin/brew shellenv)"'

      # Check if already in .zprofile
      if ! grep -q '/opt/homebrew/bin/brew shellenv' ~/.zprofile 2>/dev/null; then
        echo "$brew_env" >> ~/.zprofile
        log "Added Homebrew to ~/.zprofile"
      fi

      eval "$(/opt/homebrew/bin/brew shellenv)"
    fi
  fi
}

# =============================================================================
# Brew Packages
# =============================================================================
install_brew_packages() {
  section "Brew Packages"

  # Formulas (CLI tools)
  local formulas=(
    git
    neovim
    sheldon
    starship
    fzf
    sketchybar
    lua
    grep
    gh
  )

  # Casks (GUI apps)
  local casks=(
    wezterm
    aerospace
    karabiner-elements
    sf-symbols
    font-hackgen-nerd
    font-hack-nerd-font
  )

  # Get installed packages once (optimization)
  log "Checking installed packages..."
  local installed_formulas
  local installed_casks
  installed_formulas=$(brew list --formula 2>/dev/null || echo "")
  installed_casks=$(brew list --cask 2>/dev/null || echo "")

  log "Installing formulas..."
  for formula in "${formulas[@]}"; do
    if echo "$installed_formulas" | grep -q "^${formula}$"; then
      log "  $formula is already installed"
    else
      log "  Installing $formula..."
      if ! brew install "$formula"; then
        warn "Failed to install $formula"
      fi
    fi
  done

  log "Installing casks..."
  for cask in "${casks[@]}"; do
    if echo "$installed_casks" | grep -q "^${cask}$"; then
      log "  $cask is already installed"
    else
      log "  Installing $cask..."
      if ! brew install --cask "$cask"; then
        warn "Failed to install $cask"
      fi
    fi
  done
}

# =============================================================================
# Starship Prompt
# =============================================================================
setup_starship() {
  section "Starship"

  if command_exists starship; then
    log "Starship is already installed"
  else
    warn "Starship is not installed (should be installed via brew)"
  fi
}

# =============================================================================
# Sketchybar App Font
# =============================================================================
install_sketchybar_font() {
  section "Sketchybar App Font"

  local font_dir="$HOME/Library/Fonts"

  # Create font directory if not exists
  if [ ! -d "$font_dir" ]; then
    log "Creating font directory..."
    mkdir -p "$font_dir"
  fi

  # Get latest version from GitHub API
  local app_font_url
  local app_font_bg_url

  log "Fetching latest font versions..."

  # sketchybar-app-font
  app_font_url=$(curl -s https://api.github.com/repos/kvndrsslr/sketchybar-app-font/releases/latest | grep "browser_download_url.*ttf" | head -1 | cut -d '"' -f 4)
  if [ -z "$app_font_url" ]; then
    # Fallback to known version
    app_font_url="https://github.com/kvndrsslr/sketchybar-app-font/releases/download/v2.0.25/sketchybar-app-font.ttf"
    warn "Could not fetch latest version, using fallback"
  fi

  # sketchybar-app-font-bg
  app_font_bg_url=$(curl -s https://api.github.com/repos/SoichiroYamane/sketchybar-app-font-bg/releases/latest | grep "browser_download_url.*ttf" | head -1 | cut -d '"' -f 4)
  if [ -z "$app_font_bg_url" ]; then
    # Fallback to known version
    app_font_bg_url="https://github.com/SoichiroYamane/sketchybar-app-font-bg/releases/download/v0.4.6/sketchybar-app-font-bg.ttf"
    warn "Could not fetch latest version, using fallback"
  fi

  if [ -f "$font_dir/sketchybar-app-font.ttf" ]; then
    log "Sketchybar app font is already installed"
  else
    log "Installing sketchybar-app-font..."
    if ! curl -L "$app_font_url" -o "$font_dir/sketchybar-app-font.ttf"; then
      warn "Failed to install sketchybar-app-font"
    fi
  fi

  if [ -f "$font_dir/sketchybar-app-font-bg.ttf" ]; then
    log "Sketchybar app font (bg) is already installed"
  else
    log "Installing sketchybar-app-font-bg..."
    if ! curl -L "$app_font_bg_url" -o "$font_dir/sketchybar-app-font-bg.ttf"; then
      warn "Failed to install sketchybar-app-font-bg"
    fi
  fi
}

# =============================================================================
# Symlinks
# =============================================================================
create_symlinks() {
  section "Symlinks"

  if [ -f "$DOTFILES_DIR/.bin/symlink.sh" ]; then
    log "Running symlink.sh..."
    if ! bash "$DOTFILES_DIR/.bin/symlink.sh"; then
      warn "symlink.sh completed with some errors"
    fi
  else
    error "symlink.sh not found at $DOTFILES_DIR/.bin/symlink.sh"
  fi
}

# =============================================================================
# Sheldon (Zsh Plugin Manager)
# =============================================================================
setup_sheldon() {
  section "Sheldon"

  if ! command_exists sheldon; then
    warn "Sheldon is not installed, skipping..."
    return
  fi

  # Check if config exists (should be created by symlink.sh)
  if [ ! -f "$HOME/.config/sheldon/plugins.toml" ]; then
    warn "Sheldon config not found at ~/.config/sheldon/plugins.toml, skipping..."
    return
  fi

  log "Sheldon is installed, running lock..."
  if ! sheldon lock; then
    warn "Failed to run sheldon lock"
  fi
}

# =============================================================================
# Start Services
# =============================================================================
start_services() {
  section "Start Services"

  log "Starting sketchybar..."
  if ! brew services start sketchybar; then
    warn "Failed to start sketchybar"
  fi

  log "Starting AeroSpace..."
  if ! open -a AeroSpace; then
    warn "Failed to start AeroSpace"
  fi
}

# =============================================================================
# Summary
# =============================================================================
print_summary() {
  section "Setup Complete!"

  cat << 'EOF'
The following has been set up:
  ✅ Xcode Command Line Tools
  ✅ Homebrew
  ✅ CLI tools (git, neovim, sheldon, starship, fzf, sketchybar, etc.)
  ✅ GUI apps (WezTerm, AeroSpace, Karabiner-Elements)
  ✅ Fonts (HackGen Nerd, Hack Nerd Font, Sketchybar App Font)
  ✅ Symlinks
  ✅ Sheldon plugins
  ✅ Starship prompt

Next steps:
  1. Restart your terminal (or run: exec zsh)
  2. Check sketchybar and AeroSpace are running

EOF
  echo "Log file: $LOG_FILE"
}

# =============================================================================
# Main
# =============================================================================
main() {
  cat << 'EOF'

╔════════════════════════════════════════════════════════════╗
║           Dotfiles Initial Setup Script                    ║
╚════════════════════════════════════════════════════════════╝

EOF

  # Check if dotfiles directory exists
  if [ ! -d "$DOTFILES_DIR" ]; then
    error "Dotfiles directory not found at $DOTFILES_DIR"
  fi

  log "Starting installation... (Log: $LOG_FILE)"

  install_xcode_cli
  install_homebrew
  install_brew_packages
  install_sketchybar_font
  create_symlinks
  setup_sheldon      # After symlinks so config exists
  setup_starship
  start_services
  print_summary
}

# Run main function
main "$@"
