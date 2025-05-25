#!/bin/bash
# Development testing script for thinkube installer

set -e

# Ensure we're using bash regardless of user's shell
if [ -z "$BASH_VERSION" ]; then
    exec bash "$0" "$@"
fi

echo "🧪 Testing thinkube installer in development mode"
echo "================================================"

# Check if we're in the installer directory
if [[ ! -f "README.md" ]] || [[ ! -d "frontend" ]]; then
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

# Create npm wrapper for proper PATH handling
NPM_WRAPPER="$PWD/npm-wrapper.sh"

# Function to cleanup background processes
cleanup() {
    echo -e "\n🛑 Stopping all processes..."
    jobs -p | xargs -r kill 2>/dev/null || true
    
    # Also kill any lingering vite processes
    pkill -f "vite" 2>/dev/null || true
    lsof -ti:5173,5174,8000 2>/dev/null | xargs -r kill -9 2>/dev/null || true
    exit
}

# Initial cleanup of any existing processes
echo "🧹 Cleaning up any existing processes..."
pkill -f "vite" 2>/dev/null || true
pkill -f "uvicorn" 2>/dev/null || true
lsof -ti:5173,5174,8000 2>/dev/null | xargs -r kill -9 2>/dev/null || true
sleep 1

trap cleanup EXIT INT TERM

# 1. Test Backend
echo -e "\n1️⃣  Testing FastAPI Backend"
echo "------------------------"
cd backend

# Create virtual environment if it doesn't exist
if [[ ! -d "venv" ]]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate venv and install dependencies
source venv/bin/activate
echo "Installing backend dependencies..."
pip install -q -r requirements.txt

# Start backend in background
echo "Starting FastAPI backend on http://localhost:8000..."
python main.py &
BACKEND_PID=$!
sleep 3

# Test backend health
echo "Testing backend health endpoint..."
if curl -s http://localhost:8000/ | grep -q "healthy"; then
    echo "✅ Backend is running"
else
    echo "❌ Backend health check failed"
    exit 1
fi

cd ..

# 2. Test Frontend
echo -e "\n2️⃣  Testing Vue Frontend"
echo "---------------------"
cd frontend

# Install dependencies if needed
if [[ ! -d "node_modules" ]]; then
    echo "Installing frontend dependencies..."
    $NPM_WRAPPER install
fi

# Start frontend dev server in background
echo "Starting Vue dev server on http://localhost:5173..."
$NPM_WRAPPER run dev &
FRONTEND_PID=$!
sleep 5

cd ..

# 3. Test Electron (optional)
echo -e "\n3️⃣  Testing Electron App (Optional)"
echo "--------------------------------"
echo "Do you want to test the Electron app? (y/N)"
read -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    cd electron
    
    if [[ ! -d "node_modules" ]]; then
        echo "Installing Electron dependencies..."
        $NPM_WRAPPER install
    fi
    
    echo "Starting Electron app..."
    $NPM_WRAPPER run dev &
    ELECTRON_PID=$!
    
    cd ..
fi

# Display status
echo -e "\n✅ All components are running!"
echo "==============================="
echo "📡 Backend API: http://localhost:8000"
echo "📡 API Docs: http://localhost:8000/docs"
echo "🎨 Frontend: http://localhost:5173"
echo -e "\n📝 Press Ctrl+C to stop all services"

# Keep script running
wait