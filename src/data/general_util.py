import disnake
from disnake.ext import commands
import random
import collections
import sqlite3
import os
import asyncio
from dotenv import load_dotenv
from datetime import datetime, timezone
DB_PATH = os.getenv('DB_PATH')

STARTER_BALANCE = 1000

'''Reminders'''
def set_reminder(user_id: int, reminder: str, reminder_time: datetime, creation_time: datetime):
    con = sqlite3.connect(f"{DB_PATH}")
    cur = con.cursor()
    cur.execute(f'''INSERT INTO reminders (REMINDER_TARGET, REMINDER, REMINDER_TIME,CREATION_TIME) VALUES ({user_id},"{reminder}","{reminder_time}","{creation_time}");''')
    con.commit()
    con.close()

def get_reminder():
    reminders = {}
    creation_times = {}
    current_time = datetime.now().astimezone(timezone.utc).strftime("%Y:%m:%d:%H:%M")
    print(current_time)
    con = sqlite3.connect(f"{DB_PATH}")
    cur = con.cursor()
    for row in cur.execute(f'''SELECT REMINDER_TARGET,REMINDER,CREATION_TIME FROM reminders WHERE REMINDER_TIME="{current_time}";'''):
        reminders[row[0]] = row[1]
        creation_times[row[0]] = row[2]
    con.commit()
    con.close()
    return reminders, creation_times
    

'''Polls'''
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


'''User Descriptions'''
def init_user_description(user_id: int):
    con = sqlite3.connect(f"{DB_PATH}")
    cur = con.cursor()
    cur.execute(f'''INSERT INTO user_descriptions (USER_ID) VALUES ({user_id});''')
    con.commit()
    con.close()

def get_user_description(user_id: int):
    con = sqlite3.connect(f"{DB_PATH}")
    cur = con.cursor()
    description = cur.execute(f'''SELECT USER_DESCRIPTION FROM user_descriptions WHERE USER_ID={user_id};''').fetchone()
    if description is None:
        init_user_description(user_id)
        description = cur.execute(f'''SELECT USER_DESCRIPTION FROM user_descriptions WHERE USER_ID={user_id};''').fetchone()
    con.commit()
    con.close()
    return description[0]

def set_user_description(user_id: int, new_description: str):
    con = sqlite3.connect(f"{DB_PATH}")
    cur = con.cursor()
    cur.execute(f'''DELETE FROM user_descriptions WHERE USER_ID={user_id};''')
    cur.execute(f'''INSERT INTO user_descriptions (USER_ID,USER_DESCRIPTION) VALUES ({user_id},"{new_description}")''')
    con.commit()
    con.close()


'''Honkai Data'''
def set_honkai_user_info(user_id: int, ltuid: int, ltoken: str, honkai_uid: int):
    con = sqlite3.connect(f"{DB_PATH}")
    cur = con.cursor()
    cur.execute(f'''DELETE FROM honkai_user_info WHERE USER_ID={user_id};''')
    cur.execute(f'''INSERT INTO honkai_user_info (USER_ID,LTUID,LTOKEN,HONKAI_UID) VALUES ({user_id},{ltuid},"{ltoken}",{honkai_uid});''')
    con.commit()
    con.close()

def get_honkai_user_info(user_id: int):
    con = sqlite3.connect(f"{DB_PATH}")
    cur = con.cursor()
    row = cur.execute(f'''SELECT LTUID,LTOKEN,HONKAI_UID FROM honkai_user_info WHERE USER_ID={user_id};''').fetchone()
    if row is None:
        return None
    con.commit()
    con.close()
    return row


'''YouTube'''
def check_video_id(video_id: str):
    con = sqlite3.connect(f"{DB_PATH}")
    cur = con.cursor()
    video_data = cur.execute(f'''SELECT VIDEO_ID FROM latest_videos WHERE VIDEO_ID="{video_id}";''').fetchone()
    if video_data is None:
        return None
    con.commit()
    con.close()
    return video_data[0]

def add_video_id(video_id: str):
    con = sqlite3.connect(f"{DB_PATH}")
    cur = con.cursor()
    cur.execute(f'''INSERT INTO latest_videos (VIDEO_ID) VALUES ("{video_id}");''').fetchone()
    con.commit()
    con.close()
    
    
'''Twitter'''
def check_tweet_id(tweet_id: str):
    con = sqlite3.connect(f"{DB_PATH}")
    cur = con.cursor()
    tweet_data = cur.execute(f'''SELECT TWEET_ID FROM latest_tweets WHERE TWEET_ID="{tweet_id}";''').fetchone()
    if tweet_data is None:
        return None
    con.commit()
    con.close()
    return tweet_data[0]

def add_tweet_id(tweet_id: str):
    con = sqlite3.connect(f"{DB_PATH}")
    cur = con.cursor()
    cur.execute(f'''INSERT INTO latest_tweets (TWEET_ID) VALUES ("{tweet_id}");''').fetchone()
    con.commit()
    con.close()