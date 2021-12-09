import mysql.connector


print('Running Python')

mydb = mysql.connector.connect(
  host="localhost",
  port="",
  user="yourusername",
  password="yourpassword",
  database="mydatabase"
)

mycursor = mydb.cursor()

mycursor.execute("SELECT * FROM customers")

myresult = mycursor.fetchall()

for x in myresult:
    print(x)



