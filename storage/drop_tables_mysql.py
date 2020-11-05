import mysql.connector

db_conn = mysql.connector.connect(host="kafka-service-based.westus2.cloudapp.azure.com", user="root",
                                  password="password", database="events")

db_cursor = db_conn.cursor()

db_cursor.execute('''
	DROP TABLE facts, user
''')

db_conn.commit()
db_conn.close()
