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

# cur.execute('''CREATE TABLE genshin
#                (ID INTEGER PRIMARY KEY,
#                USER_ID INT NOT NULL, 
#                ITEM TEXT NOT NULL,
#                AMOUNT INT DEFAULT 1,
#                ITEM_TYPE INT NOT NULL);''')

cur.execute('''CREATE TABLE economy
               (ID INTEGER PRIMARY KEY,
               USER_ID INT NOT NULL, 
               BALANCE INT DEFAULT 0);''')

#FIGURE THIS OUT 
cur.execute('''CREATE TABLE coinflip
               (GAME_ID INTEGER PRIMARY KEY,
               USER_ID INT NOT NULL);''')

con.commit()
con.close()