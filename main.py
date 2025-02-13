import datetime
import sqlite3
import time
import pywinctl
import os

def initialStartup():
    os.remove("time_tracker.db")
    if not os.path.exists("time_tracker.db"):
        conn = sqlite3.connect("time_tracker.db",)
        cur = conn.cursor()
        cur.execute('''CREATE TABLE APP_IDS (
                    app_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    app_name varchar(255) NOT NULL
                    )''')
        cur.execute('''CREATE TABLE TIME_LOG (
                    log_id INTEGER PRIMARY KEY AUTOINCREMENT, 
                    app_id INTEGER NOT NULL,
                    start_time DATETIME,
                    end_time DATETIME,
                    time_used INTEGER NOT NULL,
                    FOREIGN KEY(app_id) REFERENCES APP_IDS(app_id)
                    )''')
        conn.close()
    pass



def trackWindowChanges():
    """Continuously monitors for active window changes."""
    last_app = None
    start_time = datetime.datetime.now()


    while True:
        active_window = pywinctl.getActiveWindow()
        active_app = active_window.getAppName()
        active_title = active_window.title if active_window else "No Active Window"


        if last_app != active_app and active_title is not None:
            onWindowChange(last_app,start_time,datetime.datetime.now())
            start_time = datetime.datetime.now()
            last_app = active_app

        
        time.sleep(1)  


def onWindowChange(app_name,start_time,end_time):
    if app_name is not None:
        start_time.strftime('%Y-%m-%d %H:%M:%S') 
        print(start_time.strftime('%Y-%m-%d %H:%M:%S') )
        print(app_name," used for ", end_time-start_time)
        # add into database and check app_name for app_id

        conn = sqlite3.connect("time_tracker.db",)
        cur = conn.cursor()
        #app id
        cur.execute(f'SELECT app_id FROM APP_IDS WHERE app_name LIKE "{app_name}"')
        if cur.fetchone() is None:
            cur.execute("INSERT INTO APP_IDS (app_name) VALUES (?)", (app_name,))
            conn.commit()
            time.sleep(0.5)
        cur.execute(f"SELECT app_id FROM APP_IDS WHERE app_name LIKE '{app_name}'")
        print(cur.fetchall())




initialStartup()
# Start tracking
trackWindowChanges()
