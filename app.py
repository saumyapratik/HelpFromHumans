from flask import Flask, render_template, request, redirect, session, g
import sqlite3

app = Flask(__name__)
app.secret_key = "secretkey"

# 🔹 DATABASE CONFIG
DATABASE = "helpfromhumans.db"

# 🔹 DATABASE CONNECTION
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row  # access columns by name
    return db

# 🔹 CLOSE DATABASE CONNECTION
@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

# 🔹 INITIALIZE DATABASE TABLES
def init_db():
    conn = get_db()
    cur = conn.cursor()

    # Users table
    cur.execute('''CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL
                   )''')

    # Questions table
    cur.execute('''CREATE TABLE IF NOT EXISTS questions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user TEXT NOT NULL,
                    question TEXT NOT NULL
                   )''')

    # Answers table
    cur.execute('''CREATE TABLE IF NOT EXISTS answers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    question_id INTEGER NOT NULL,
                    user TEXT NOT NULL,
                    answer TEXT NOT NULL,
                    FOREIGN KEY(question_id) REFERENCES questions(id)
                   )''')

    conn.commit()
    # Questions table
    cur.execute('''CREATE TABLE IF NOT EXISTS questions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user TEXT NOT NULL,
                    question TEXT NOT NULL
                   )''')
    # Answers table
    cur.execute('''CREATE TABLE IF NOT EXISTS answers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    question_id INTEGER NOT NULL,
                    user TEXT NOT NULL,
                    answer TEXT NOT NULL,
                    FOREIGN KEY(question_id) REFERENCES questions(id)
                   )''')
    conn.commit()

# 🔹 HOME PAGE
@app.route('/')
def home():
    return render_template('index.html')

# 🔹 LOGIN PAGE
@app.route('/login')
def login():
    return render_template('login.html')

# 🔹 LOGIN POST
@app.route('/login', methods=['POST'])
def login_post():
    username = request.form['username']
    password = request.form['password']

    conn = get_db()
    cur = conn.cursor()

    # Fetch user from database
    cur.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
    user = cur.fetchone()

    if user:
        session['user'] = username
        return redirect('/dashboard')
    else:
        # Invalid login
        return "Invalid username or password. Try again."

# 🔹 SIGNUP PAGE
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db()
        cur = conn.cursor()

        # Check if username already exists
        cur.execute("SELECT * FROM users WHERE username = ?", (username,))
        existing_user = cur.fetchone()

        if existing_user:
            # You can show an error message here (optional)
            return "Username already exists! Please choose another."

        # Insert new user into users table
        cur.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        conn.commit()

        # Log the user in automatically after signup
        session['user'] = username
        return redirect('/dashboard')

    return render_template('signup.html')

# 🔹 DASHBOARD PAGE
@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect('/login')

    conn = get_db()
    cur = conn.cursor()

    # Fetch all questions
    cur.execute("SELECT * FROM questions")
    questions_data = cur.fetchall()

    questions = []
    for q in questions_data:
        # Fetch answers for each question
        cur.execute("SELECT * FROM answers WHERE question_id = ?", (q['id'],))
        answers_data = cur.fetchall()
        answers = [{"user": ans['user'], "answer": ans['answer']} for ans in answers_data]

        questions.append({
            "id": q['id'],
            "user": q['user'],
            "question": q['question'],
            "answers": answers
        })

    return render_template('dashboard.html', questions=questions)

# 🔹 ASK QUESTION
@app.route('/ask', methods=['GET', 'POST'])
def ask():
    if 'user' not in session:
        return redirect('/login')

    if request.method == 'POST':
        question = request.form['question']
        conn = get_db()
        cur = conn.cursor()
        cur.execute("INSERT INTO questions (user, question) VALUES (?, ?)", (session['user'], question))
        conn.commit()
        return redirect('/dashboard')

    return render_template('ask.html')

# 🔹 ANSWER QUESTION
@app.route('/answer/<int:q_id>', methods=['POST'])
def answer(q_id):
    if 'user' not in session:
        return redirect('/login')

    answer_text = request.form['answer']
    conn = get_db()
    cur = conn.cursor()
    cur.execute("INSERT INTO answers (question_id, user, answer) VALUES (?, ?, ?)",
                (q_id, session['user'], answer_text))
    conn.commit()
    return redirect('/dashboard')

# 🔹 DELETE QUESTION
@app.route('/delete/<int:q_id>', methods=['POST'])
def delete(q_id):
    if 'user' not in session:
        return redirect('/login')

    conn = get_db()
    cur = conn.cursor()

    # Check if the logged-in user owns the question
    cur.execute("SELECT user FROM questions WHERE id = ?", (q_id,))
    question = cur.fetchone()

    if question and question['user'] == session['user']:
        # Delete answers first
        cur.execute("DELETE FROM answers WHERE question_id = ?", (q_id,))
        # Delete question
        cur.execute("DELETE FROM questions WHERE id = ?", (q_id,))
        conn.commit()

    return redirect('/dashboard')

# 🔹 RUN SERVER
if __name__ == '__main__':
    with app.app_context():
        init_db()  # 🔹 Create tables if not exist
    app.run(debug=True)