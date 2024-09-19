#!/bin/sh
pkill -f /home/blacknand/programming/rpi-space-dashboard-new/interface.py
source /home/blacknand/programming/rpi-space-dashboard-new/env/bin/activate
python3 /home/blacknand/programming/rpi-space-dashboard-new/interface.py
echo "Restart script ran at $(date)" >> /home/blacknand/programming/rpi-space-dashboard-new/cron_test.log 2>&1
