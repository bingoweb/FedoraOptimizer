#!/bin/bash
# Fedora Optimizer - Intelligent Auto-Bootstrap Launcher
# Automatically handles dependencies and environment setup

# Ensure we are in the script directory
cd "$(dirname "$0")"

# ------------------------------------------------------------------------------
# 1. ROOT CHECK
# ------------------------------------------------------------------------------
if [ "$EUID" -ne 0 ]; then
    echo "⚠️  This tool requires root privileges for system optimization."
    echo "🔑 Requesting sudo access..."
    exec sudo "$0" "$@"
fi

# ------------------------------------------------------------------------------
# 2. DEPENDENCY CHECK & AUTO-INSTALL
# ------------------------------------------------------------------------------
echo "🔍 Checking system environment..."

# Function to check and install a system package
ensure_pkg() {
    if ! command -v "$1" &> /dev/null; then
        echo "📦 Installing missing system tool: $1 ($2)..."
        dnf install -y "$2" > /dev/null 2>&1
        if [ $? -eq 0 ]; then
            echo "   ✅ Installed $2"
        else
            echo "   ❌ Failed to install $2. Please install manually."
        fi
    fi
}

# Check essential tools
ensure_pkg "python3" "python3"
ensure_pkg "pip" "python3-pip"
ensure_pkg "lspci" "pciutils"
ensure_pkg "dmidecode" "dmidecode"
ensure_pkg "nmcli" "NetworkManager"

# Check Python Libraries (rich, psutil)
# We try to import them to verify they are actually usable
echo "🔍 Verifying Python libraries..."

MISSING_LIBS=0
python3 -c "import rich" 2>/dev/null || MISSING_LIBS=1
python3 -c "import psutil" 2>/dev/null || MISSING_LIBS=1

if [ $MISSING_LIBS -eq 1 ]; then
    echo "📦 Missing Python dependencies detected."
    echo "⏳ Installing required libraries (rich, psutil)..."
    pip3 install rich psutil > /dev/null 2>&1
    
    # Double check
    if python3 -c "import rich; import psutil" 2>/dev/null; then
        echo "   ✅ Libraries installed successfully."
    else
        echo "   ❌ Failed to install Python libraries."
        echo "   👉 Try running: sudo pip3 install rich psutil"
        read -p "Press Enter to exit..."
        exit 1
    fi
else
    echo "   ✅ All Python dependencies are present."
fi


# ------------------------------------------------------------------------------
# 3. EXECUTION
# ------------------------------------------------------------------------------

# Check if in development mode
if [ "${DEV_MODE:-0}" = "1" ] || [ "${DEBUG_MODE:-0}" = "1" ]; then
    echo "🐛 Development/Debug Mode Active"
    echo "📊 Launching debug console in background..."
    
    # Try to open debug monitor in new terminal window
    MONITOR_CMD="cd $(pwd) && ./debug_monitor.sh; echo 'Monitor exited'; read -p 'Enter to close...' "
    
    if command -v konsole &> /dev/null; then
        konsole --new-tab -e bash -c "$MONITOR_CMD" &
    elif command -v gnome-terminal &> /dev/null; then
        gnome-terminal -- bash -c "$MONITOR_CMD" &
    elif command -v xterm &> /dev/null; then
        xterm -e "$MONITOR_CMD" &
    fi
    sleep 1
    
    echo "🚀 Launching Application..."
    DEBUG_MODE=1 python3 src/ui/tui_app.py
else
    # Production Launch
    python3 src/ui/tui_app.py
fi

# Prevent terminal closure on error
EXIT_CODE=$?
if [ $EXIT_CODE -ne 0 ]; then
    echo ""
    echo "❌ Application exited with error code: $EXIT_CODE"
    echo "   Check debug.log for details."
    echo ""
    read -p "Press Enter to exit..."
fi
