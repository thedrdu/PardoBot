import sqlite3

con = sqlite3.connect('database.db')
print("Successful connection to database.")
cur = con.cursor()

cur.execute('''DELETE FROM latest_videos;''')
con.commit()
con.close()