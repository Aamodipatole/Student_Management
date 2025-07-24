from flask import Flask, render_template, request, redirect, send_file
import sqlite3
import csv
from threading import Thread
import webview

app = Flask(__name__)

def init_db():
    conn = sqlite3.connect('students.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS students
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  name TEXT NOT NULL,
                  roll TEXT NOT NULL,
                  course TEXT NOT NULL)''')
    conn.commit()
    conn.close()

@app.route('/')
def index():
    query = request.args.get('q', '')
    conn = sqlite3.connect('students.db')
    c = conn.cursor()
    if query:
        c.execute("SELECT * FROM students WHERE name LIKE ? OR roll LIKE ? OR course LIKE ?", 
                  (f'%{query}%', f'%{query}%', f'%{query}%'))
    else:
        c.execute("SELECT * FROM students")
    students = c.fetchall()
    conn.close()
    return render_template('index.html', students=students, query=query)

@app.route('/add', methods=['POST'])
def add_student():
    name = request.form['name']
    roll = request.form['roll']
    course = request.form['course']
    conn = sqlite3.connect('students.db')
    c = conn.cursor()
    c.execute("INSERT INTO students (name, roll, course) VALUES (?, ?, ?)", (name, roll, course))
    conn.commit()
    conn.close()
    return redirect('/')

@app.route('/delete/<int:id>')
def delete_student(id):
    conn = sqlite3.connect('students.db')
    c = conn.cursor()
    c.execute("DELETE FROM students WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return redirect('/')

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_student(id):
    conn = sqlite3.connect('students.db')
    c = conn.cursor()
    if request.method == 'POST':
        name = request.form['name']
        roll = request.form['roll']
        course = request.form['course']
        c.execute("UPDATE students SET name=?, roll=?, course=? WHERE id=?", (name, roll, course, id))
        conn.commit()
        conn.close()
        return redirect('/')
    else:
        c.execute("SELECT * FROM students WHERE id=?", (id,))
        student = c.fetchone()
        conn.close()
        return render_template('edit.html', student=student)

@app.route('/export')
def export_students():
    conn = sqlite3.connect('students.db')
    c = conn.cursor()
    c.execute("SELECT * FROM students")
    rows = c.fetchall()
    conn.close()
    csv_file = 'students_export.csv'
    with open(csv_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['ID', 'Name', 'Roll', 'Course'])
        writer.writerows(rows)
    return send_file(csv_file, as_attachment=True)

def start_flask():
    app.run(debug=False, port=5000)

if __name__ == '__main__':
    init_db()
    Thread(target=start_flask).start()
    webview.create_window("Student Management System", "http://127.0.0.1:5000/", width=900, height=600, resizable=False)
    webview.start()
