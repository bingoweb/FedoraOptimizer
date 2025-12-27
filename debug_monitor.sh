#!/bin/bash
# ML-Enhanced Debug Monitor v3.0
# Real-time error tracking with ML analysis visualization

# Enhanced Colors
CRITICAL='\033[1;41m'  # Red background
RED='\033[1;31m'
GREEN='\033[1;32m'
YELLOW='\033[1;33m'
BLUE='\033[1;34m'
CYAN='\033[1;36m'
MAGENTA='\033[1;35m'
WHITE='\033[1;37m'
GRAY='\033[0;90m'
ORANGE='\033[0;33m'
PURPLE='\033[0;35m'
NC='\033[0m'

LOG_FILE="debug.log"
ERROR_FILE="errors_only.log"

# Clear screen
clear

echo -e "${CYAN}╔══════════════════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║         FEDORA OPTIMIZER - ML-ENHANCED DEBUG CONSOLE v3.0                   ║${NC}"
echo -e "${CYAN}║                   🤖 Machine Learning Error Analysis                         ║${NC}"
echo -e "${CYAN}╚══════════════════════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${WHITE}📊 Monitoring:${NC}"
echo -e "   ${YELLOW}Full Log:${NC} ${LOG_FILE}"
echo -e "   ${YELLOW}Errors Only:${NC} ${ERROR_FILE}"
echo ""
echo -e "${WHITE}🤖 ML Features:${NC}"
echo -e "   ${PURPLE}●${NC} Error Pattern Detection"
echo -e "   ${PURPLE}●${NC} Severity Analysis (0-10)"
echo -e "   ${PURPLE}●${NC} Smart Fix Suggestions"
echo -e "   ${PURPLE}●${NC} Root Cause Detection"
echo -e "   ${PURPLE}●${NC} Performance Anomaly Detection"
echo -e "   ${PURPLE}●${NC} Recurring Error Tracking"
echo ""
echo -e "${WHITE}🔍 Detection Levels:${NC}"
echo -e "   ${RED}●${NC} Critical (9-10)  ${ORANGE}●${NC} High (7-8)  ${YELLOW}●${NC} Medium (5-6)  ${GREEN}●${NC} Low (1-4)"
echo ""
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${WHITE}Waiting for application...${NC}"
echo ""

# Wait for log file
while [ ! -f "$LOG_FILE" ]; do
    sleep 0.3
done

echo -e "${GREEN}✓ Application started! ML Analysis active...${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Advanced color highlighting with ML markers
tail -f "$LOG_FILE" | while IFS= read -r line; do
    # ML Analysis markers - Purple
    if [[ $line == *"🤖 ML"* ]] || [[ $line == *"ML ANALİZİ"* ]]; then
        echo -e "${PURPLE}${line}${NC}"
    
    # Severity markers
    elif [[ $line == *"Severity: 10"* ]] || [[ $line == *"Severity: 9"* ]]; then
        echo -e "${CRITICAL}${line}${NC}"
    elif [[ $line == *"Severity: 8"* ]] || [[ $line == *"Severity: 7"* ]]; then
        echo -e "${RED}${line}${NC}"
    elif [[ $line == *"Severity: 6"* ]] || [[ $line == *"Severity: 5"* ]]; then
        echo -e "${YELLOW}${line}${NC}"
    
    # Fix suggestions - Bright Cyan
    elif [[ $line == *"💡 ÖNERİLEN ÇÖZÜM"* ]] || [[ $line == *"suggestion"* ]]; then
        echo -e "${CYAN}${line}${NC}"
    
    # Root cause - Bright Yellow
    elif [[ $line == *"🔍 OLASI NEDEN"* ]] || [[ $line == *"Root Cause"* ]]; then
        echo -e "${YELLOW}${line}${NC}"
    
    # Recurring indicator - Orange
    elif [[ $line == *"Recurring: EVET"* ]] || [[ $line == *"daha önce görüldü"* ]]; then
        echo -e "${ORANGE}${line}${NC}"
    
    # Critical errors - Red background
    elif [[ $line == *"💥 CRITICAL"* ]] || [[ $line == *"UNCAUGHT EXCEPTION"* ]]; then
        echo -e "${CRITICAL}${line}${NC}"
    
    # Exception errors - Bright Red
    elif [[ $line == *"❌ EXCEPTION"* ]] || [[ $line == *"Error Type:"* ]] || [[ $line == *"Exception Type:"* ]]; then
        echo -e "${RED}${line}${NC}"
    
    # Regular errors
    elif [[ $line == *"❌"* ]] || [[ $line == *"ERROR"* ]]; then
        echo -e "${RED}${line}${NC}"
    
    # Success
    elif [[ $line == *"✅"* ]] || [[ $line == *"SUCCESS"* ]]; then
        echo -e "${GREEN}${line}${NC}"
    
    # Warnings
    elif [[ $line == *"⚠️"* ]] || [[ $line == *"WARNING"* ]]; then
        echo -e "${YELLOW}${line}${NC}"
    
    # Performance anomaly
    elif [[ $line == *"🐌 PERFORMANCE ANOMALY"* ]]; then
        echo -e "${ORANGE}${line}${NC}"
    elif [[ $line == *"🐌"* ]] || [[ $line == *"SLOW"* ]]; then
        echo -e "${ORANGE}${line}${NC}"
    
    # Menu selection
    elif [[ $line == *"📌 MENU"* ]] || [[ $line == *"####"* ]]; then
        echo -e "${MAGENTA}${line}${NC}"
    
    # Function entry
    elif [[ $line == *"🟢 FUNCTION ENTRY"* ]]; then
        echo -e "${BLUE}${line}${NC}"
    
    # Operations
    elif [[ $line == *"🔵"* ]] || [[ $line == *"OPERATION"* ]]; then
        echo -e "${CYAN}${line}${NC}"
    
    # Debug info
    elif [[ $line == *"🔍"* ]] || [[ $line == *"DEBUG"* ]]; then
        echo -e "${GRAY}${line}${NC}"
    
    # Info
    elif [[ $line == *"ℹ️"* ]] || [[ $line == *"INFO"* ]]; then
        echo -e "${WHITE}${line}${NC}"
    
    # Separators
    elif [[ $line == *"===="* ]] || [[ $line == *"----"* ]]; then
        echo -e "${CYAN}${line}${NC}"
    
    # Stack traces
    elif [[ $line == *"File \""* ]] || [[ $line == *"Traceback"* ]]; then
        echo -e "\033[2;31m${line}${NC}"
    
    # Local variables
    elif [[ $line =~ "   [a-zA-Z_]+ =" ]]; then
        echo -e "\033[2;33m${line}${NC}"
    
    # Default
    else
        echo "$line"
    fi
done
