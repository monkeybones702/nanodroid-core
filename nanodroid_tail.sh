#!/bin/bash
LOG_FILE="$HOME/.nanodroid_engine.log"

if [ -f "$LOG_FILE" ]; then
    # Extract last 20 lines, display them, and pipe into termux-clipboard-set
    tail -n 20 "$LOG_FILE" | tee /dev/tty | termux-clipboard-set
    echo -e "\n[+] Status: Log output (last 20 lines) automatically copied to clipboard!"
else
    echo "[!] Error: Engine log not found at $LOG_FILE"
fi
