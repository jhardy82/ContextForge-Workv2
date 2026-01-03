import sqlite3

conn = sqlite3.connect(r'C:\Users\James\Documents\Github\GHrepos\SCCMScripts\db\taskman.db')
print('Projects:', conn.execute('SELECT COUNT(*) FROM projects').fetchone()[0])
print('Sprints:', conn.execute('SELECT COUNT(*) FROM sprints').fetchone()[0])
print('Tasks:', conn.execute('SELECT COUNT(*) FROM tasks').fetchone()[0])
conn.close()
