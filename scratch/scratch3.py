import sqlite3

con = sqlite3.connect("test.db")

cur = con.cursor()


#cur.execute("CREATE TABLE movie(title, year, score)")
cur.execute("INSERT INTO movie VALUES ('title', 1975, 5.5), ('second_title', 2004, 6)")
result = cur.execute("SELECT * FROM movie")

res = result.fetchall()
print(res)

con.commit()