#!/usr/bin/data/data/com.termux/files/usr/bin/bash

# Read the latest clipboard content using termux-api
CMD=$(termux-clipboard-get)

if [ -n "$CMD" ]; then
    echo -e "\033[1;32m[+] Executing Clipboard Command:\033[0m"
    echo "$CMD"
chmod +x ~/.termux/tasker/run_clipboard.sh
    echo "----------------------------------------"
    eval "$CMD"
else
    echo "[-] Clipboard is empty."
fi


