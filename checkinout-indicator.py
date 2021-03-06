#!/usr/bin/env python

import signal

from gi.repository import Gtk as gtk
from gi.repository import AppIndicator3 as appindicator
from gi.repository import Notify as notify
from gi.repository import GLib

from threading import Thread
from datetime import datetime
import os
import time
import math

APPINDICATOR_ID = 'checkinout-indicator'
duration1 = 7*60*60 # First warning duration (in seconds)
duration2 = 9*60*60 # Second warning duration (in seconds)

def main():
    global indicator
    indicator = appindicator.Indicator.new(APPINDICATOR_ID, 'tray-extended-away', appindicator.IndicatorCategory.SYSTEM_SERVICES)
    indicator.set_status(appindicator.IndicatorStatus.ACTIVE)
    indicator.set_menu(build_menu())
    
    notify.init(APPINDICATOR_ID)
    update_indicator()
    gtk.main()
    

def checkin_time():
    if os.path.isfile('todays_uptime'):
        if os.stat("todays_uptime").st_size != 0:
            uptime_seconds = get_uptime()
        else:
            uptime_seconds = write_system_boot_time()
    else:
        uptime_seconds = write_system_boot_time()
    return uptime_seconds

def write_system_boot_time():
    boot_date_time = str(time.time())
    t = open('todays_uptime', 'w')
    t.write(boot_date_time)
    t.close()
    return 0.0

def get_uptime():
    with open('todays_uptime', 'r') as f:
        system_boot_time = float(f.readline().split()[0])
        if datetime.fromtimestamp(system_boot_time).date() != datetime.now().date():
            return write_system_boot_time()
        else:
            return time.time() - system_boot_time

def time_to_text(t):
    hours = int(math.floor(t / 60 / 60))
    mins = int(round(t / 60) - (hours*60))
    text = ''
    if hours > 0:
        text = str(hours) + ' hours '
    text = text + str(mins) + ' minutes'
    return text

def update_indicator():
    rem_time1 = duration1 - checkin_time()
    rem_time2 = duration2 - checkin_time()

    if rem_time2 < 0:
        text = 'Leave NOW!'
    elif rem_time1 < 0:
        text = time_to_text(rem_time2)
    else:
        text = time_to_text(rem_time1)

    if rem_time1 < 0:
        text = 'Full-day | ' + text

    if rem_time2 < 0:
        text = 'Overtime | ' + text

    indicator.set_label(text, '')
    GLib.timeout_add(1000, update_indicator)

def build_menu():
    menu = gtk.Menu()
    checkin_time_str = time.strftime('%H:%M%p', time.localtime(time.time()-checkin_time()))
    item = gtk.MenuItem('Check-in Time:' + checkin_time_str)
    menu.append(item)
    menu.show_all()
    return menu

def quit(_):
    notify.uninit()
    gtk.main_quit()

if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    main()
