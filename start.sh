#!/bin/bash

# Check if file exists
if [ -f "hotmail_checker_bot.py" ]; then
    echo "✅ Found hotmail_checker_bot.py"
    python3 hotmail_checker_bot.py
elif [ -f "/app/hotmail_checker_bot.py" ]; then
    echo "✅ Found /app/hotmail_checker_bot.py"
    cd /app
    python3 hotmail_checker_bot.py
else
    echo "❌ File not found! Listing files:"
    ls -la
    pwd
    exit 1
fi
