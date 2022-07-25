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

# cur.execute('''CREATE TABLE reminders
#             (REMINDER_ID INTEGER PRIMARY KEY,
#             REMINDER_TARGET INT NOT NULL,
#             REMINDER TEXT DEFAULT "",
#             REMINDER_TIME DATETIME,
#             CREATION_TIME DATETIME);''')

# cur.execute('''CREATE TABLE rpg_stats
#             (USER_ID INTEGER NOT NULL,
#             EXP INTEGER NOT NULL DEFAULT 0,
#             ATTACK INTEGER NOT NULL DEFAULT 1,
#             DEFENSE INTEGER NOT NULL DEFAULT 0,
#             DEXTERITY INTEGER NOT NULL DEFAULT 1,
#             LUCK INTEGER NOT NULL DEFAULT 1,
#             COINS INTEGER NOT NULL DEFAULT 0,
#             MAX_HP INTEGER NOT NULL DEFAULT 10);''')

# cur.execute('''CREATE TABLE enemies
#             (ENEMY_ID INTEGER PRIMARY KEY,
#             LEVEL INTEGER NOT NULL DEFAULT 1,
#             ATTACK INTEGER NOT NULL DEFAULT 1,
#             DEFENSE INTEGER NOT NULL DEFAULT 0,
#             LUCK INTEGER NOT NULL DEFAULT 1,
#             HP INTEGER NOT NULL DEFAULT 5);''')

# cur.execute('''CREATE TABLE polls
#             (POLL_ID INTEGER PRIMARY KEY,
#             POLL_TITLE TEXT);''')

# cur.execute('''CREATE TABLE poll_options
#             (OPTION_ID INTEGER PRIMARY KEY,
#             POLL_ID INTEGER NOT NULL,
#             OPTION_TITLE TEXT);''')

# cur.execute('''CREATE TABLE poll_votes
#             (VOTE_ID INTEGER PRIMARY KEY,
#             POLL_ID INTEGER NOT NULL,
#             OPTION_ID INTEGER NOT NULL,
#             USER_ID INTEGER);''')

# cur.execute('''CREATE TABLE user_descriptions
#             (ID INTEGER PRIMARY KEY,
#             USER_ID INTEGER NOT NULL,
#             USER_DESCRIPTION TEXT DEFAULT "Hello!");''')

# cur.execute('''CREATE TABLE honkai_user_info
#             (ID INTEGER PRIMARY KEY,
#             USER_ID INTEGER NOT NULL,
#             LTUID INTEGER NOT NULL,
#             LTOKEN INTEGER NOT NULL,
#             HONKAI_UID INTEGER NOT NULL);''')

cur.execute('''CREATE TABLE latest_videos
            (ID INTEGER PRIMARY KEY,
            VIDEO_ID TEXT NOT NULL UNIQUE);''')

con.commit()
con.close()