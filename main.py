import datetime
from re import A
import sqlite3
import time
import pywinctl
import os
from json import dumps,loads
from collections import defaultdict
from icoextract import IconExtractor, IconExtractorError
from PIL import Image

def string_to_datetime_object(dateString:str):
    
    # This functions is made only for the specific string that gets stored so no other use case. idk man
    f = "%Y-%m-%d %H:%M:%S"
    return datetime.datetime.strptime(dateString[:-7], f)

def get_icon_adress(exe_adress:str):

    try:
        extractor = IconExtractor(exe_adress)
        app_name = exe_adress.rstrip(".exe")
        extractor.export_icon(f'/app_icons/{app_name}.ico', num=0)
        return '/app_icons/{app_name}.ico'

    except IconExtractorError:
        pass

def initialStartup():
    # os.remove("time_tracker.db")
    if not os.path.exists("time_tracker.db"):

        conn = sqlite3.connect("time_tracker.db",)
        cur = conn.cursor()

        cur.execute('''CREATE TABLE APP_IDS (
                    app_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    app_name varchar(255) NOT NULL,
                    icon_adress TEXT 
                    )''')
        
        cur.execute('''CREATE TABLE TIME_LOG (
                    log_id INTEGER PRIMARY KEY AUTOINCREMENT, 
                    app_id INTEGER NOT NULL,
                    start_time DATETIME,
                    end_time DATETIME,
                    time_used INTEGER NOT NULL,
                    FOREIGN KEY(app_id) REFERENCES APP_IDS(app_id)
                    )''')
        
        cur.execute('''CREATE TABLE ARCHIVES (
                    log_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date DATETIME
                    )''')
        
        for i in range(24):
            cur.execute(f'''ALTER TABLE ARCHIVES ADD hour_{i} TEXT''')
        conn.close()
    pass


def logCondenser():
    """Condenses previous days logs and then drops table to clear it for todays records"""
    conn = sqlite3.connect("time_tracker.db")
    cur = conn.cursor()
    # TODO : Check date and fetch all previous day logs, condense and store in another table,then drop time_log to clear it for todays logs.
    
    today = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(today,type(today))
    




    #### FIX THE DATE PICKIUNG UP THING MAN IDK IM TOO TIRED
    cur.execute("SELECT * FROM TIME_LOG WHERE end_time < CURRENT_DATE ")
    logs = cur.fetchall()

    # Create 24 empty lists for each hour
    hourly_data = defaultdict(list)

    # Organize data by hour
    for record in logs:
        dt = datetime.datetime.fromisoformat(record[2])
        hourly_data[dt.hour].append((record[2], record))

    # Convert defaultdict to a standard list with 24 elements
    result = [hourly_data[hour] for hour in range(24)]

    
    for hour, records in enumerate(result):
        print(f"Hour {hour}: {len(records)} records")   

    placeholder  = ("?," *24).strip(',')
    result = tuple([dumps(i) for i in result])
    collumns = ""
    for i in range(24):
        collumns += f'hour_{i},' 
    collumns = collumns.rstrip(',')
    # this wont work exactly but go off ig
    yesterday = (datetime.datetime.today()-datetime.timedelta(days=1)).strftime('%Y-%m-%d')
    data = (yesterday,) +result

    cur.execute(f'''INSERT INTO ARCHIVES (date,{collumns}) VALUES (?,{placeholder})''',data)
    conn.commit()

    cur.execute('''DELETE FROM TIME_LOG WHERE end_time < date('now', 'start of day')''')
    cur.execute('''DELETE FROM sqlite_sequence WHERE name="TIME_LOG"''')
    conn.commit()

    print("done")

    
    conn.close()

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
    """Logs how long an application was used"""

    if app_name is not None:
        start_time.strftime('%Y-%m-%d %H:%M:%S') 

        conn = sqlite3.connect("time_tracker.db",)
        cur = conn.cursor()
        #app id
        cur.execute(f'SELECT app_id FROM APP_IDS WHERE app_name LIKE "{app_name}"')
        if cur.fetchone() is None:
            icon_adress = get_icon_adress(app_name)
            cur.execute("INSERT INTO APP_IDS (app_name,icon_adress) VALUES (?,?)", (app_name,icon_adress))
            conn.commit()
            
        cur.execute(f"SELECT app_id FROM APP_IDS WHERE app_name LIKE '{app_name}'")
        app_id = cur.fetchall()[0][0]


        cur.execute("INSERT INTO TIME_LOG (app_id,start_time,end_time,time_used) VALUES (?,?,?,?)",
                    (app_id,start_time,end_time,(end_time-start_time).total_seconds()))
        conn.commit()
        conn.close()
        
        print(start_time.strftime('%Y-%m-%d %H:%M:%S') )
        print(app_name," used for ", end_time-start_time)





initialStartup()
logCondenser()
# Start tracking
trackWindowChanges()
