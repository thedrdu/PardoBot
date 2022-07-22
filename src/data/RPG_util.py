import disnake
from disnake.ext import commands
import random
import collections
import sqlite3
import os
import asyncio
import math
from math import floor
from dotenv import load_dotenv

DB_PATH = os.getenv('DB_PATH')

DEFAULT_STATS = [0,1,0,1,1,0,10]

def add_exp(user_id: int, amount: int):
    con = sqlite3.connect(f"{DB_PATH}")
    cur = con.cursor()
    row = cur.execute(f'''SELECT EXP FROM rpg_stats 
                      WHERE USER_ID={user_id};''').fetchone()
    
    current_level = get_level(row[0])
    new_exp = row[0] + amount
    new_level = get_level(new_exp)
    
    cur.execute(f'''UPDATE rpg_stats SET EXP={new_exp} 
                WHERE USER_ID={user_id};''')
    con.commit()
    con.close()

# def level_up(levels: int):
#     #Increase attack

def get_level(exp: int):
    return math.floor(0.3 * math.sqrt(exp))

def progress_to_next(exp: int):
    if exp < 0:
        return 0
    level = get_level(exp)
    low = get_exp(level)
    high = get_exp(level+1)
    high -= low
    exp -= low
    print(high)
    print(exp)
    return int(100 * round(exp/high, 2))

def get_exp(level: int):
    return pow(level/0.3, 2)

def init_stats(user_id):
    con = sqlite3.connect(f"{DB_PATH}")
    cur = con.cursor()
    row = cur.execute(f'''SELECT EXP,ATTACK,DEFENSE,DEXTERITY,LUCK,COINS 
                      FROM rpg_stats 
                      WHERE USER_ID={user_id}''').fetchone()
    if row is None:
        cur.execute(f'''INSERT INTO rpg_stats (USER_ID,EXP,ATTACK,DEFENSE,DEXTERITY,LUCK,COINS,MAX_HP) 
                    VALUES ({user_id},0,1,0,1,1,0,10);''')
    con.commit()
    con.close()

def get_stats(user_id: int):
    con = sqlite3.connect(f"{DB_PATH}")
    cur = con.cursor()
    row = cur.execute(f'''SELECT EXP,ATTACK,DEFENSE,DEXTERITY,LUCK,COINS,MAX_HP 
                      FROM rpg_stats 
                      WHERE USER_ID={user_id}''').fetchone()
    if row is None:
        con.commit()
        con.close()
        init_stats(user_id)
        return DEFAULT_STATS
    con.commit()
    con.close()
    return row

def add_enemy(name: str, stats):
    con = sqlite3.connect(f"{DB_PATH}")
    cur = con.cursor()
    cur.execute(f'''INSERT INTO enemies (LEVEL,ATTACK,DEFENSE,LUCK,HP) 
                    VALUES ({stats[0]},{stats[1]},{stats[2]},{stats[3]},{stats[4]});''')
    con.commit()
    con.close()
    return cur.lastrowid
    

def get_enemy_stats(enemy_id: int):
    con = sqlite3.connect(f"{DB_PATH}")
    cur = con.cursor()
    row = cur.execute(f'''SELECT LEVEL,ATTACK,DEFENSE,LUCK,HP 
                      FROM enemies 
                      WHERE ENEMY_ID={enemy_id}''').fetchone()
    con.commit()
    con.close()
    return row