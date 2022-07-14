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

def get_global_rank(user_id):
    '''
    Checks the number of people with balances higher than the target user, then adds 1(since rankings are not 0-indexed)
    '''
    con = sqlite3.connect(f"{DB_PATH}")
    cur = con.cursor()
    rows = cur.execute(f'''SELECT count(*) FROM economy WHERE balance > (SELECT balance FROM economy WHERE user_id={user_id});''')
    row_count = rows.fetchone()[0]
    con.commit()
    con.close()
    print(row_count)
    return row_count+1

def get_global_rank(user_id):
    '''
    Checks the number of people with balances higher than the target user globally, then adds 1(since rankings are not 0-indexed)
    '''
    con = sqlite3.connect(f"{DB_PATH}")
    cur = con.cursor()
    rows = cur.execute(f'''SELECT count(*) FROM economy WHERE balance > (SELECT balance FROM economy WHERE user_id={user_id});''')
    row_count = rows.fetchone()[0]
    con.commit()
    con.close()
    print(row_count)
    return row_count+1

def get_server_rank(user_id, guild):
    '''
    Checks the number of people with balances higher than the target user in the server, then adds 1(since rankings are not 0-indexed)
    '''
    member_list_string = ','.join([str(elem.id) for elem in guild.members])
    con = sqlite3.connect(f"{DB_PATH}")
    cur = con.cursor()
    rows = cur.execute(f'''SELECT count(*) FROM economy WHERE balance > (SELECT balance FROM economy WHERE user_id={user_id}) 
                       AND USER_ID IN ({member_list_string});''')
    row_count = rows.fetchone()[0]
    con.commit()
    con.close()
    print(row_count)
    return row_count+1