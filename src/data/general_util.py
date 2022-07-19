import disnake
from disnake.ext import commands
import random
import collections
import sqlite3
import os
import asyncio
from dotenv import load_dotenv
from datetime import datetime
DB_PATH = os.getenv('DB_PATH')

STARTER_BALANCE = 1000

def set_reminder(user_id: int, reminder: str, reminder_time: datetime):
    con = sqlite3.connect(f"{DB_PATH}")
    cur = con.cursor()
    cur.execute(f'''INSERT INTO reminders (REMINDER_TARGET, REMINDER, REMINDER_TIME) VALUES ({user_id},"{reminder}","{reminder_time}");''')
    con.commit()
    con.close()

def get_reminder():
    output = {}
    current_time = datetime.now().strftime("%Y:%m:%d:%H:%M")
    print(current_time)
    con = sqlite3.connect(f"{DB_PATH}")
    cur = con.cursor()
    for row in cur.execute(f'''SELECT REMINDER_TARGET,REMINDER FROM reminders WHERE REMINDER_TIME="{current_time}";'''):
        output[row[0]] = row[1]
    con.commit()
    con.close()
    return output
    
