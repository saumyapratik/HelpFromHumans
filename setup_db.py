import sqlite3

# Connect to (or create) the database file
conn = sqlite3.connect('database.db')
cur = conn.cursor()

# Create 'questions' table
cur.execute("""
CREATE TABLE IF NOT EXISTS questions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user TEXT NOT NULL,
    question TEXT NOT NULL
)
""")

# Create 'answers' table
cur.execute("""
CREATE TABLE IF NOT EXISTS answers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    question_id INTEGER NOT NULL,
    user TEXT NOT NULL,
    answer TEXT NOT NULL,
    FOREIGN KEY (question_id) REFERENCES questions(id)
)
""")

conn.commit()
conn.close()

print("Database and tables created successfully!")