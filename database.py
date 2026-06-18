import sqlite3

conn = sqlite3.connect('student.db')

cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS student_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    subject TEXT,
    study_hours INTEGER,
    sleep_hours INTEGER,
    screen_time INTEGER,
    attendance INTEGER,
    productivity REAL
)
''')

conn.commit()
conn.close()

print("Database Created Successfully!")