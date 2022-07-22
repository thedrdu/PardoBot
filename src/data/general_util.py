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

def set_reminder(user_id: int, reminder: str, reminder_time: datetime, creation_time: datetime):
    con = sqlite3.connect(f"{DB_PATH}")
    cur = con.cursor()
    cur.execute(f'''INSERT INTO reminders (REMINDER_TARGET, REMINDER, REMINDER_TIME,CREATION_TIME) VALUES ({user_id},"{reminder}","{reminder_time}","{creation_time}");''')
    con.commit()
    con.close()

def get_reminder():
    reminders = {}
    creation_times = {}
    current_time = datetime.now().strftime("%Y:%m:%d:%H:%M")
    print(current_time)
    con = sqlite3.connect(f"{DB_PATH}")
    cur = con.cursor()
    for row in cur.execute(f'''SELECT REMINDER_TARGET,REMINDER,CREATION_TIME FROM reminders WHERE REMINDER_TIME="{current_time}";'''):
        reminders[row[0]] = row[1]
        creation_times[row[0]] = row[2]
    con.commit()
    con.close()
    return reminders, creation_times
    
def create_poll(title: str):
    con = sqlite3.connect(f"{DB_PATH}")
    cur = con.cursor()
    cur.execute(f'''INSERT INTO polls (POLL_TITLE) 
                VALUES ("{title}");''')
    con.commit()
    con.close()
    return cur.lastrowid

def insert_option(poll_id: int, option_title: str):
    con = sqlite3.connect(f"{DB_PATH}")
    cur = con.cursor()
    cur.execute(f'''INSERT INTO poll_options (POLL_ID,OPTION_TITLE) VALUES ({poll_id},"{option_title}");''')
    con.commit()
    con.close()
    return cur.lastrowid

def remove_vote(poll_id: int, user_id: int):
    con = sqlite3.connect(f"{DB_PATH}")
    cur = con.cursor()
    cur.execute(f'''DELETE FROM poll_votes WHERE POLL_ID={poll_id} AND USER_ID={user_id}''')
    con.commit()
    con.close()
    
def add_vote(poll_id: int, option_id: int, user_id: int):
    con = sqlite3.connect(f"{DB_PATH}")
    cur = con.cursor()
    cur.execute(f'''INSERT INTO poll_votes (POLL_ID,OPTION_ID,USER_ID) VALUES ({poll_id},{option_id},{user_id});''')
    con.commit()
    con.close()
    
def get_options(poll_id: int):
    options = {}
    con = sqlite3.connect(f"{DB_PATH}")
    cur = con.cursor()
    rows = cur.execute(f'''SELECT OPTION_ID,OPTION_TITLE FROM poll_options WHERE POLL_ID={poll_id}''')
    for row in rows:
        options[row[0]] = row[1]
    con.commit()
    con.close()
    return options

def get_votes(option_id: int):
    con = sqlite3.connect(f"{DB_PATH}")
    cur = con.cursor()
    votes = cur.execute(f'''SELECT count(*) FROM poll_votes WHERE OPTION_ID={option_id};''').fetchone()[0]
    con.commit()
    con.close()
    return votes