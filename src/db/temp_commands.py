import sqlite3

con = sqlite3.connect('database.db')
print("Successful connection to database.")
cur = con.cursor()

cur.execute('''DROP TABLE poll_votes;''')
con.commit()
con.close()