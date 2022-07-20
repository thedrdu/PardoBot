import sqlite3

con = sqlite3.connect('database.db')
print("Successful connection to database.")
cur = con.cursor()

# cur.execute('''CREATE TABLE blackjack
#                (GAME_ID INTEGER PRIMARY KEY,
#                PLAYER_ID INTEGER NOT NULL, 
#                PLAYER_CARDS TEXT DEFAULT "", 
#                DEALER_CARDS TEXT DEFAULT "", 
#                GAME_STATE BOOLEAN DEFAULT 1);''')

# cur.execute('''CREATE TABLE genshin_wishes
#                (ID INTEGER PRIMARY KEY,
#                USER_ID INT NOT NULL, 
#                ITEM TEXT NOT NULL);''')

# cur.execute('''CREATE TABLE economy
#                (ID INTEGER PRIMARY KEY,
#                USER_ID INT NOT NULL, 
#                BALANCE INT DEFAULT 0);''')

# #FIGURE THIS OUT 
# cur.execute('''CREATE TABLE roulette
#                (ID INTEGER PRIMARY KEY,
#                GAME_ID INTEGER NOT NULL,
#                USER_ID INTEGER NOT NULL);''')

# cur.execute('''CREATE TABLE genshin_pity
#             (ID INTEGER PRIMARY KEY,
#             USER_ID INT NOT NULL,
#             PITY5 INT NOT NULL,
#             PITY4 INT NOT NULL);''')

# cur.execute('''CREATE TABLE rps
#             (ID INTEGER PRIMARY KEY,
#             GAME_ID INT NOT NULL,
#             USER_ID INT NOT NULL,
#             CHOICE TEXT NOT NULL);''')

cur.execute('''CREATE TABLE reminders
            (REMINDER_ID INTEGER PRIMARY KEY,
            REMINDER_TARGET INT NOT NULL,
            REMINDER TEXT DEFAULT "",
            REMINDER_TIME DATETIME,
            CREATION_TIME DATETIME);''')

con.commit()
con.close()