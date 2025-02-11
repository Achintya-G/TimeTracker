import datetime
import sqlite3
import time
import pywinctl


def dbconn():
    conn = sqlite3.connect("time_tracker.db",)
    cur = conn.cursor()
    conn.close()

d = pywinctl.getAllAppsWindowsTitles()  # to get all applications open
for i in d:
    print(i, len(d[i]))

while True:
    time.sleep(1)
    print(pywinctl.getActiveWindow().getAppName())  # to get focused app name