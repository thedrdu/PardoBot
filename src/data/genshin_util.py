import disnake
from disnake.ext import commands
import random
import collections
import sqlite3
import os
import asyncio
from dotenv import load_dotenv
DB_PATH = os.getenv('DB_PATH')

def insert_pull(user_id: int, pull: str):
    con = sqlite3.connect(f"{DB_PATH}")
    cur = con.cursor()
    cur.execute(f'''INSERT INTO genshin_wishes (USER_ID, ITEM) VALUES ({user_id},"{pull}");''')
    con.commit()
    con.close()
    
def get_pulls(user_id: int):
    output = []
    con = sqlite3.connect(f"{DB_PATH}")
    cur = con.cursor()
    rows = cur.execute(f'''SELECT ITEM FROM genshin_wishes WHERE USER_ID={user_id};''')
    items = rows.fetchall()
    con.commit()
    con.close()
    for item in items:
        output.append(item[0])
    return output

def reset_pulls(user_id: int):
    con = sqlite3.connect(f"{DB_PATH}")
    cur = con.cursor()
    cur.execute(f'''DELETE FROM genshin_wishes WHERE USER_ID={user_id};''')
    con.commit()
    con.close()



def get_pity(user_id: int):
    con = sqlite3.connect(f"{DB_PATH}")
    cur = con.cursor()
    rows = cur.execute(f'''SELECT PITY5,PITY4 FROM genshin_pity WHERE USER_ID={user_id};''')
    pity = rows.fetchone()
    if pity is None:
        cur.execute(f'''INSERT INTO genshin_pity (USER_ID,PITY5,PITY4) VALUES ({user_id},0,0);''')
        con.commit()
        con.close()
        print("inserting fresh")
        return 0,0
    con.commit()
    con.close()
    return pity

def set_pity5(user_id: int, pity5: int):
    con = sqlite3.connect(f"{DB_PATH}")
    cur = con.cursor()
    cur.execute(f'''UPDATE genshin_pity SET PITY5={pity5} WHERE USER_ID={user_id};''')
    con.commit()
    con.close()

def set_pity4(user_id: int, pity4: int):
    con = sqlite3.connect(f"{DB_PATH}")
    cur = con.cursor()
    cur.execute(f'''UPDATE genshin_pity SET PITY4={pity4} WHERE USER_ID={user_id};''')
    con.commit()
    con.close()