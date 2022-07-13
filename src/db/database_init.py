import sqlite3

con = sqlite3.connect('database.db')
print("Successful connection to database.")
cur = con.cursor()

cur.execute('''CREATE TABLE blackjack
               (GAME_ID INTEGER PRIMARY KEY,
               PLAYER_ID INTEGER NOT NULL, 
               PLAYER_CARDS TEXT DEFAULT "", 
               DEALER_CARDS TEXT DEFAULT "", 
               GAME_STATE BOOLEAN DEFAULT 1);''')