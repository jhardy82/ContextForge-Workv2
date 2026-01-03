import sqlite3

conn = sqlite3.connect('taskman.db')
print('Projects:', conn.execute('SELECT COUNT(*) FROM projects').fetchone()[0])
print('Sprints:', conn.execute('SELECT COUNT(*) FROM sprints').fetchone()[0])
print('Tasks:', conn.execute('SELECT COUNT(*) FROM tasks').fetchone()[0])
conn.close()
