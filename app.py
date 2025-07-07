from flask import Flask, render_template, request, redirect
import sqlite3
import os

app = Flask(__name__)
DB_FILE = "database.db"

def init_db():
    if not os.path.exists(DB_FILE):
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS contacts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL,
                message TEXT NOT NULL
            )
        ''')
        conn.commit()
        conn.close()

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/contact', methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        message = request.form["message"]

        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("INSERT INTO contacts (name, email, message) VALUES (?, ?, ?)",
                  (name, email, message))
        conn.commit()
        conn.close()

        return redirect("/thankyou")
    return render_template("contact.html")

@app.route('/thankyou')
def thank_you():
    return "<h2>Thank you for contacting me!</h2>"

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)
