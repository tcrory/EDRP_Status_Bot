#! /bin/sh

sleep 60

cd /home/pi

su -c "/usr/bin/python3.5 /home/pi/edrp_status_bot/edrp_status_bot.py" - pi
