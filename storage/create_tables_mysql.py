import mysql.connector

db_conn = mysql.connector.connect(host="kafka-service-based.westus2.cloudapp.azure.com", user="root",
                                  password="password", database="events")

db_cursor = db_conn.cursor()

db_cursor.execute('''
	CREATE TABLE facts
	(id INT NOT NULL AUTO_INCREMENT,
	fact_id VARCHAR(250) NOT NULL,
	user_id VARCHAR(250) NOT NULL,
	fact VARCHAR(250) NOT NULL,
	tags VARCHAR(250) NOT NULL,
	timestamp VARCHAR(100) NOT NULL,
	date_added VARCHAR(100) NOT NULL,
	CONSTRAINT facts_pk PRIMARY KEY(id))
''')

db_cursor.execute('''
	CREATE TABLE user
	(id INT NOT NULL AUTO_INCREMENT,
	user_id VARCHAR(250) NOT NULL,
	username VARCHAR(250) NOT NULL,
	timestamp VARCHAR(100) NOT NULL,
	date_created VARCHAR(100) NOT NULL,
	subscribed BOOLEAN NOT NULL,
	CONSTRAINT user_pk PRIMARY KEY (id))
''')

db_conn.commit()
db_conn.close()
