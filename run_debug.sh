#!/bin/bash
# Debug Mode Launcher
# Runs FedoraOptimizer with DEBUG_MODE enabled

echo "🐛 Starting Fedora Optimizer in DEBUG MODE..."
echo "📊 Logs will be written to: debug.log"
echo ""
echo "💡 TIP: Open another terminal and run: ./debug_monitor.sh"
echo ""
sleep 2

# Set debug mode and run
DEBUG_MODE=1 sudo -E python3 src/ui/tui_app.py
