import sqlite3

con = sqlite3.connect('database.db')
print("Successful connection to database.")
cur = con.cursor()

# cur.execute('''DELETE FROM blackjack;''')
# cur.execute('''DELETE FROM economy;''')
# cur.execute('''DELETE FROM roulette;''')
cur.execute('''DROP TABLE latest_videos''')
con.commit()
con.close()