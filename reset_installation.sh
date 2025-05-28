#\!/bin/bash
# Reset script to clean up installation state

echo "🔄 Resetting Thinkube installation state..."
echo "=========================================="

# 1. Stop any running installer processes
echo "1️⃣ Stopping installer processes..."
pkill -f "test-dev" 2>/dev/null || true
pkill -f "vite" 2>/dev/null || true
pkill -f "uvicorn" 2>/dev/null || true
pkill -f "electron" 2>/dev/null || true
lsof -ti:5173,5174,8000 2>/dev/null  < /dev/null |  xargs -r kill -9 2>/dev/null || true

# 2. Clear installer state files
echo "2️⃣ Clearing installer state..."
cd /home/thinkube/thinkube/installer
rm -f frontend/.installer-state.json
rm -f backend/.installer-state.json

# 3. Clear browser storage (if using Electron)
echo "3️⃣ Clearing Electron cache..."
rm -rf electron/.config 2>/dev/null || true

# 4. Reset network configuration to original state
echo "4️⃣ Resetting network configuration..."
sudo rm -f /etc/netplan/99-installer-*.yaml
sudo netplan apply

# 5. Remove any temporary inventory files
echo "5️⃣ Cleaning temporary files..."
rm -f /tmp/inventory-*.yaml
rm -f /tmp/ansible-*.log

# 6. Ensure GPU drivers are correct
echo "6️⃣ Checking GPU drivers..."
if lspci -k | grep -A3 "VGA" | grep -q "vfio-pci"; then
    echo "   ⚠️  GPUs still bound to vfio-pci, fixing..."
    sudo /usr/local/bin/fix-gpu-binding.sh 2>/dev/null || echo "   ℹ️  Manual GPU fix may be needed"
fi

# 7. Clear any failed systemd services
echo "7️⃣ Resetting failed services..."
sudo systemctl reset-failed

# 8. Ensure display manager is running
echo "8️⃣ Checking display manager..."
if ! systemctl is-active --quiet gdm; then
    sudo systemctl restart gdm 2>/dev/null || sudo systemctl restart lightdm 2>/dev/null || true
fi

echo ""
echo "✅ Reset complete!"
echo ""
echo "You can now start the installer fresh by:"
echo "1. Opening a terminal on the desktop (not SSH)"
echo "2. Running:"
echo "   cd ~/thinkube/installer"
echo "   ./test-dev.sh"

# Optional: Show system status
echo ""
echo "📊 Current system status:"
systemctl is-system-running || true
echo ""
echo "🖥️  GPU status:"
nvidia-smi -L 2>/dev/null || echo "NVIDIA driver not loaded"
