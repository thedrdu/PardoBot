import disnake
from disnake.ext import commands
import random
import collections
import sqlite3
import os
import asyncio
from dotenv import load_dotenv
DB_PATH = os.getenv('DB_PATH')

STARTER_BALANCE = 1000

def init_balance(user_id):
    con = sqlite3.connect(f"{DB_PATH}")
    cur = con.cursor()
    cur.execute(f'''INSERT INTO economy (USER_ID, BALANCE) VALUES ({user_id},{STARTER_BALANCE})''')
    con.commit()
    con.close()

def update_balance(user_id, amount):
    con = sqlite3.connect(f"{DB_PATH}")
    cur = con.cursor()
    row = cur.execute(f'''SELECT BALANCE FROM economy WHERE USER_ID={user_id};''')
    # Find way to handle if user does not have a current entry
    current_balance = row.fetchone()
    if current_balance is None:
        con.commit()
        con.close()
        init_balance(user_id)
        return STARTER_BALANCE
    current_balance = current_balance[0]
    print(f"Current balance: {current_balance}")
    print(f"Update Amount: {amount}")
    current_balance += amount
    cur.execute(f'''UPDATE economy SET BALANCE={current_balance} WHERE USER_ID={user_id};''')
    con.commit()
    con.close()

def get_balance(user_id):
    con = sqlite3.connect(f"{DB_PATH}")
    cur = con.cursor()
    row = cur.execute(f'''SELECT BALANCE FROM economy WHERE USER_ID={user_id};''')
    current_balance = row.fetchone()
    if current_balance is None:
        con.commit()
        con.close()
        init_balance(user_id)
        return STARTER_BALANCE
    current_balance = current_balance[0]
    con.commit()
    con.close()
    return current_balance