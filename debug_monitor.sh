#!/bin/bash
# Debug Monitor - Chrome DevTools benzeri konsol
# Ayrı terminalde çalıştır: ./debug_monitor.sh

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

LOG_FILE="debug.log"

# Clear screen
clear

echo -e "${CYAN}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║       FEDORA OPTIMIZER - DEBUG CONSOLE (DevTools)         ║${NC}"
echo -e "${CYAN}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${YELLOW}📊 Monitoring: ${LOG_FILE}${NC}"
echo -e "${YELLOW}🔄 Real-time updates (Ctrl+C to quit)${NC}"
echo ""
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Wait for log file to be created
while [ ! -f "$LOG_FILE" ]; do
    echo -e "${YELLOW}⏳ Waiting for app to start...${NC}"
    sleep 1
done

# Tail with color highlighting
tail -f "$LOG_FILE" | while IFS= read -r line; do
    # Color coding based on content
    if [[ $line == *"❌ HATA"* ]] || [[ $line == *"ERROR"* ]]; then
        echo -e "${RED}${line}${NC}"
    elif [[ $line == *"✅ BAŞARILI"* ]] || [[ $line == *"SUCCESS"* ]]; then
        echo -e "${GREEN}${line}${NC}"
    elif [[ $line == *"⚠️"* ]] || [[ $line == *"WARNING"* ]]; then
        echo -e "${YELLOW}${line}${NC}"
    elif [[ $line == *"📌 MENÜ"* ]]; then
        echo -e "${CYAN}${line}${NC}"
    elif [[ $line == *"🟢 BAŞLADI"* ]]; then
        echo -e "${BLUE}${line}${NC}"
    elif [[ $line == *"DEBUG"* ]]; then
        echo -e "\033[0;90m${line}${NC}"  # Gray
    else
        echo "$line"
    fi
done
