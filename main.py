import datetime
import sqlite3
import time
import pywinctl


def trackWindowChanges():
    """Continuously monitors for active window changes."""
    last_window = None


    while True:
        active_window = pywinctl.getActiveWindow()
        active_title = active_window.title if active_window else "No Active Window"

        if active_title != last_window and active_title is not None:
            print("Window changed to:", active_title)
            onWindowChange(active_window.getAppName(),datetime.datetime.now())
            last_window = active_title
        

        time.sleep(1)  


def onWindowChange(appName,timestamp):
    print(appName)
    pass


def active():
    global window
    print("ac called")
    global windowWatcher
    print(window.getAppName())# to get focused app name
    windowWatcher.stop()

def dbconn():
    conn = sqlite3.connect("time_tracker.db",)
    cur = conn.cursor()
    conn.close()


# Start tracking
trackWindowChanges()
