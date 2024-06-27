#!/bin/bash

# # Update the system
# sudo cp linuxbot.sh /usr/local/bin/linuxbot.sh && sudo chmod +x /usr/local/bin/linuxbot.sh

# Run the application (change path as needed)
cd ~/_DEV/_INTERNAL/LinuxBot/app/core

export PYTHONPATH=~/_DEV/_INTERNAL/LinuxBot/

python3 run.py
