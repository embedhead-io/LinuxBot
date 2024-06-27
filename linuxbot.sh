#!/bin/bash

# # Update the system
# sudo cp linuxbot.sh /usr/local/bin/linuxbot.sh && sudo chmod +x /usr/local/bin/linuxbot.sh

# Run the application (change path as needed)
export PYTHONPATH=~/_DEV/_INTERNAL/LinuxBot/
cd ~/_DEV/_INTERNAL/LinuxBot/app/core
python3 run.py
