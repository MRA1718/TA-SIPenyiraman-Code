import mysql.connector

mydb = mysql.connector.connect(
    host="localhost",
    user="rpi4db",
    password="sqlrpi4",
    database="rpi4watering"
)

mycursor = mydb.cursor()
tokensql = "SELECT token_telegram FROM Telegram"
mycursor.execute(tokensql)
tokentl = mycursor.fetchall()
print(tokentl[1][0])