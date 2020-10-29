import sqlite3

conn = sqlite3.connect('interesting_facts.sqlite')

c = conn.cursor()
c.execute('''
          DROP TABLE facts
          ''')
c.execute('''
          DROP TABLE user
          ''')

conn.commit()
conn.close()
