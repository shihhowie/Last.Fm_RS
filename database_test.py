import mysql.connector

mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  passwd="howard11122",
  database = "lastfm"
)

mycursor = mydb.cursor()
mycursor.execute("CREATE TABLE user (name VARCHAR(255), address VARCHAR(255))")

for x in mycursor:
	print(x)

mydb.commit()