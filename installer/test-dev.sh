#!/bin/bash
# Development testing script for thinkube installer

set -e

# Ensure we're using bash regardless of user's shell
if [ -z "$BASH_VERSION" ]; then
    exec bash "$0" "$@"
fi

# Parse command line arguments
CLEAN_STATE=false
SKIP_CONFIG=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --clean-state)
            CLEAN_STATE=true
            shift
            ;;
        --skip-config)
            SKIP_CONFIG=true
            shift
            ;;
        -h|--help)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --clean-state    Clean deployment state but preserve inventory.yaml"
            echo "  --skip-config    Skip configuration screens and use existing inventory.yaml"
            echo "  -h, --help       Show this help message"
            echo ""
            echo "Examples:"
            echo "  $0 --clean-state --skip-config   # Start fresh deployment with existing config"
            echo "  $0 --skip-config                  # Resume deployment with existing config"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

echo "🧪 Testing thinkube installer in development mode"
echo "================================================"

# Clean state if requested
if [ "$CLEAN_STATE" = true ]; then
    echo "🧹 Cleaning deployment state (preserving inventory)..."
    
    # Clean Tauri app data (localStorage/sessionStorage)
    if [ -d "$HOME/.config/thinkube-installer" ]; then
        echo "  - Removing Tauri app data directory..."
        rm -rf "$HOME/.config/thinkube-installer"
    fi
    
    # Clean backend deployment state file
    if [ -f "$HOME/.thinkube-installer/deployment-state.json" ]; then
        echo "  - Removing backend deployment state file..."
        rm -f "$HOME/.thinkube-installer/deployment-state.json"
    fi
    
    # Note: We intentionally DO NOT remove inventory.yaml
    # This allows --clean-state and --skip-config to work together
    
    echo "✅ Deployment state cleaned (inventory.yaml preserved)"
    echo ""
fi

# Check if we're in the installer directory
if [[ ! -f "package.json" ]] || [[ ! -d "frontend" ]]; then
    echo "❌ Please run this script from the installer directory"
    exit 1
fi

# Setup Node.js environment
echo "Setting up Node.js environment..."

# Check for nvm in common locations and set up PATH
NVM_DIRS=("$HOME/.nvm" "$HOME/.local/share/nvm")
NODE_FOUND=false

for nvm_dir in "${NVM_DIRS[@]}"; do
    if [ -d "$nvm_dir/v22.16.0" ]; then
        echo "🔧 Found Node v22.16.0 at $nvm_dir"
        export PATH="$nvm_dir/v22.16.0/bin:$PATH"
        NODE_FOUND=true
        break
    fi
done

# Check if node and npm are available
if ! command -v node &> /dev/null || ! command -v npm &> /dev/null; then
    echo "❌ Node.js or npm not found in PATH"
    echo "Please ensure Node.js and npm are properly installed"
    echo "Current PATH: $PATH"
    exit 1
fi

echo "✅ Node $(node --version) and npm $(npm --version) detected"

# Store the node/npm paths for use in subshells
export NODE_BIN=$(which node)
export NPM_BIN=$(which npm)

# Function to cleanup background processes
cleanup() {
    echo -e "\n🛑 Stopping all processes..."
    
    # Kill all child processes
    jobs -p | xargs -r kill -TERM 2>/dev/null || true
    sleep 1
    jobs -p | xargs -r kill -9 2>/dev/null || true
    
    # Kill specific processes
    pkill -f "vite" 2>/dev/null || true
    pkill -f "tauri" 2>/dev/null || true
    pkill -f "cargo.*tauri" 2>/dev/null || true
    pkill -f "python.*main.py" 2>/dev/null || true
    
    # Force kill anything on the ports
    lsof -ti:5173,8000 2>/dev/null | xargs -r kill -9 2>/dev/null || true
    
    # Give processes time to die
    sleep 2
    
    exit
}

# Initial cleanup of any existing processes
echo "🧹 Cleaning up any existing processes..."
pkill -f "vite" 2>/dev/null || true
pkill -f "tauri" 2>/dev/null || true
pkill -f "uvicorn" 2>/dev/null || true
lsof -ti:5173,5174,8000 2>/dev/null | xargs -r kill -9 2>/dev/null || true
sleep 1

trap cleanup EXIT INT TERM

# 1. Backend Setup (don't start it, just prepare)
echo -e "\n1️⃣  Preparing FastAPI Backend"
echo "------------------------"
cd backend

# Use a different venv name to avoid masking the installer's ~/.venv
BACKEND_VENV="venv-test"

# Create virtual environment if it doesn't exist
if [[ ! -d "$BACKEND_VENV" ]]; then
    echo "Creating Python virtual environment for testing..."
    python3 -m venv "$BACKEND_VENV"
fi

# Activate venv and install dependencies
source "$BACKEND_VENV/bin/activate"
echo "Installing backend dependencies..."
pip install -q -r requirements.txt
deactivate

echo "✅ Backend is ready (will be started by Tauri)"

cd ..

# 2. Test Tauri App
echo -e "\n2️⃣  Testing Tauri App"
echo "---------------------------------------"
echo "Do you want to test the Tauri app? (y/N)"
read -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    # Check for required system dependencies
    echo "Checking system dependencies..."
    
    MISSING_DEPS=()
    
    # Check for each required package (Tauri v2 requirements)
    for pkg in build-essential curl wget file libxdo-dev libssl-dev libwebkit2gtk-4.1-dev libayatana-appindicator3-dev librsvg2-dev; do
        if ! dpkg -l | grep -q "^ii  $pkg"; then
            MISSING_DEPS+=("$pkg")
        fi
    done
    
    if [ ${#MISSING_DEPS[@]} -ne 0 ]; then
        echo "❌ Missing system dependencies: ${MISSING_DEPS[*]}"
        echo ""
        echo "Please install them with:"
        echo "   sudo apt update && sudo apt install -y ${MISSING_DEPS[*]}"
        echo ""
        echo "These packages are required for Tauri v2:"
        echo "   - build-essential: Compiler toolchain"
        echo "   - curl, wget, file: Basic utilities"
        echo "   - libxdo-dev: X11 automation library"
        echo "   - libssl-dev: OpenSSL development headers"
        echo "   - libwebkit2gtk-4.1-dev: WebKit rendering engine"
        echo "   - libayatana-appindicator3-dev: System tray support"
        echo "   - librsvg2-dev: SVG rendering for icons"
        exit 1
    fi
    
    echo "✅ All system dependencies are installed"
    
    # Source Rust environment if it exists
    if [ -f "$HOME/.cargo/env" ]; then
        source "$HOME/.cargo/env"
    fi
    
    # Check if Rust is installed
    if ! command -v cargo &> /dev/null; then
        echo "❌ Rust/Cargo not found. Please install Rust first:"
        echo "   curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh"
        echo ""
        echo "After installation, restart your terminal or run:"
        echo "   source $HOME/.cargo/env"
        exit 1
    fi
    
    echo "✅ Rust $(cargo --version) detected"
    
    # Install dependencies if needed
    if [[ ! -d "node_modules" ]]; then
        echo "Installing dependencies..."
        npm install
    fi
    
    echo "Starting Tauri app..."
    echo "This will start both the frontend and Tauri in one command"
    # Disable GPU compositing to fix window display issues on some systems
    export WEBKIT_DISABLE_COMPOSITING_MODE=1
    # Additional environment variables for better compatibility
    export WEBKIT_DISABLE_DMABUF_RENDERER=1
    export GDK_BACKEND=x11
    
    # Pass skip-config flag to the app if requested
    if [ "$SKIP_CONFIG" = true ]; then
        export SKIP_CONFIG=true
        echo "📋 Skip configuration mode enabled"
    fi
    
    npm run dev &
    TAURI_PID=$!
    
    # Display status
    echo -e "\n✅ Tauri app is starting!"
    echo "==============================="
    echo "🖥️  Tauri will:"
    echo "   - Start the backend API on http://localhost:8000"
    echo "   - Start the Vue frontend on http://localhost:5173"
    echo "   - Open the app window"
    echo -e "\n📝 Press Ctrl+C to stop all services"
else
    # If not testing Tauri, just run the frontend separately
    echo -e "\n2️⃣  Testing Vue Frontend Only"
    echo "-------------------------"
    cd frontend
    
    if [[ ! -d "node_modules" ]]; then
        echo "Installing frontend dependencies..."
        npm install
    fi
    
    echo "Starting Vue dev server on http://localhost:5173..."
    npm run dev &
    FRONTEND_PID=$!
    
    cd ..
    
    # Display status
    echo -e "\n✅ Components are running!"
    echo "==============================="
    echo "📡 Backend API: http://localhost:8000"
    echo "📡 API Docs: http://localhost:8000/docs"
    echo "🎨 Frontend: http://localhost:5173"
    echo -e "\n📝 Press Ctrl+C to stop all services"
fi

# Keep script running
wait