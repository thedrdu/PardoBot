import sqlite3

con = sqlite3.connect('database.db')
print("Successful connection to database.")
cur = con.cursor()

cur.execute('''DROP TABLE blackjack;''')
cur.execute('''DROP TABLE economy;''')
con.commit()
con.close()