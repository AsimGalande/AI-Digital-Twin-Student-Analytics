from flask import Flask, render_template, request, redirect, session
import sqlite3
import matplotlib.pyplot as plt

app = Flask(__name__)
app.secret_key = "asim123"

@app.route('/', methods=['GET', 'POST'])
def home():

    result = ""

    if request.method == 'POST':

        subject = request.form['subject']
        hours = int(request.form['hours'])
        difficulty = request.form['difficulty']

        study_hours = int(request.form.get('study_hours', 0))
        sleep_hours = int(request.form.get('sleep_hours', 0))
        screen_time = int(request.form.get('screen_time', 0))
        attendance = int(request.form.get('attendance', 0))
        exam_score = int(request.form.get('exam_score', 0))

        # Study Plan
        if difficulty == "Easy":
            daily = max(1, hours // 2)
        elif difficulty == "Medium":
            daily = max(1, hours // 3)
        else:
            daily = max(1, hours // 4)

        # Productivity Score
        productivity = (
            study_hours * 5
            + sleep_hours * 3
            + attendance * 0.3
            - screen_time * 2
        )

        # Status
        if productivity >= 80:
            status = "Excellent"
        elif productivity >= 60:
            status = "Good"
        elif productivity >= 40:
            status = "Average"
        else:
            status = "Needs Improvement"

        # Burnout Detection
        if sleep_hours < 6 and screen_time > 5:
            burnout = "High Risk"
        elif sleep_hours < 7 or screen_time > 4:
            burnout = "Moderate Risk"
        else:
            burnout = "Low Risk"

        # Advice
        advice = ""

        if sleep_hours < 7:
            advice += "Sleep more. "

        if screen_time > 4:
            advice += "Reduce screen time. "

        if study_hours < 4:
            advice += "Increase study hours. "

        if attendance < 75:
            advice += "Improve attendance. "

        if advice == "":
            advice = "Keep up the good work!"

        # Exam Prediction
        predicted_score = (
            exam_score * 0.5
            + study_hours * 4
            + attendance * 0.2
            + sleep_hours
            - screen_time
        )

        predicted_score = min(100, max(0, predicted_score))

        # Save to Database
        conn = sqlite3.connect('student.db')
        cursor = conn.cursor()

        cursor.execute("""
        INSERT INTO student_data
        (subject, study_hours, sleep_hours, screen_time, attendance, productivity)
        VALUES (?, ?, ?, ?, ?, ?)
        """, (
            subject,
            study_hours,
            sleep_hours,
            screen_time,
            attendance,
            productivity
        ))

        conn.commit()
        conn.close()

        result = f"""
Subject: {subject}

Total Hours Required: {hours}

Difficulty: {difficulty}

Recommended Daily Study: {daily} hours/day

Study Hours Today: {study_hours}

Sleep Hours: {sleep_hours}

Screen Time: {screen_time}

Attendance: {attendance}%

Productivity Score: {productivity:.1f}

Status: {status}

Burnout Risk: {burnout}

Predicted Next Exam Score: {predicted_score:.1f}

Advice: {advice}
"""

    return render_template('index.html', result=result)


@app.route('/history')
def history():

    conn = sqlite3.connect('student.db')
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM student_data")
    data = cursor.fetchall()

    conn.close()

    return render_template('history.html', data=data)


@app.route('/dashboard')
def dashboard():

    conn = sqlite3.connect('student.db')
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM student_data")
    total_entries = cursor.fetchone()[0]

    cursor.execute("SELECT AVG(productivity) FROM student_data")
    avg_productivity = cursor.fetchone()[0]

    cursor.execute("SELECT MAX(productivity) FROM student_data")
    max_productivity = cursor.fetchone()[0]

    cursor.execute("SELECT MIN(productivity) FROM student_data")
    min_productivity = cursor.fetchone()[0]

    conn.close()

    return render_template(
        'dashboard.html',
        total_entries=total_entries,
        avg_productivity=avg_productivity,
        max_productivity=max_productivity,
        min_productivity=min_productivity
    )


@app.route('/graph')
def graph():

    conn = sqlite3.connect('student.db')
    cursor = conn.cursor()

    cursor.execute("SELECT productivity FROM student_data")
    data = cursor.fetchall()

    conn.close()

    scores = [row[0] for row in data]

    plt.figure(figsize=(8, 5))
    plt.plot(scores, marker='o')
    plt.title("Productivity Trend")
    plt.xlabel("Entry Number")
    plt.ylabel("Productivity Score")
    plt.grid(True)

    plt.savefig("static/productivity.png")
    plt.close()

    return render_template('graph.html')

@app.route('/register', methods=['GET', 'POST'])
def register():

    if request.method == 'POST':

        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO users(username, password) VALUES(?, ?)",
            (username, password)
        )

        conn.commit()
        conn.close()

        return redirect('/login')

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM users WHERE username=? AND password=?",
            (username, password)
        )

        user = cursor.fetchone()

        conn.close()

        if user:
            session['user'] = username
            return redirect('/')

    return render_template('login.html')

@app.route('/logout')
def logout():

    session.pop('user', None)

    return redirect('/login')

import os

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)