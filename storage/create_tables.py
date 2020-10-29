import sqlite3

conn = sqlite3.connect('interesting_facts.sqlite')

c = conn.cursor()
c.execute('''
		  CREATE TABLE facts
		  (id INTEGER PRIMARY KEY ASC,
		   fact_id VARCHAR(250) NOT NULL,
		   user_id VARCHAR(250) NOT NULL,
		   fact VARCHAR(250) NOT NULL,
		   tags VARCHAR(250) NOT NULL,
			timestamp VARCHAR(100) NOT NULL,
		   date_added VARCHAR(100) NOT NULL
		   )
		  ''')

c.execute('''
		  CREATE TABLE user
		  (id INTEGER PRIMARY KEY ASC,
		   user_id VARCHAR(250) NOT NULL,
		   username VARCHAR(250) NOT NULL,
			timestamp VARCHAR(100) NOT NULL,
		   date_created VARCHAR(100) NOT NULL,
		   subscribed BOOLEAN NOT NULL
		   )
		  ''')

conn.commit()
conn.close()
