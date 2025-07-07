from flask import Flask, render_template, request, redirect
import sqlite3
import os
from flask_mail import Mail, Message
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)
DB_FILE = "database.db"

# ----- Flask-Mail Config -----
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')  # your_email@gmail.com
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')  # your App Password
app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_USERNAME')  # ensures sender is defined

mail = Mail(app)

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

        # Save to DB
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("INSERT INTO contacts (name, email, message) VALUES (?, ?, ?)",
                  (name, email, message))
        conn.commit()
        conn.close()

        # Send Email Notification
        try:
            msg = Message(
                subject="📩 New Contact Submission",
                recipients=[app.config['MAIL_USERNAME']],  # send to yourself
                body=f"New message from:\n\nName: {name}\nEmail: {email}\n\nMessage:\n{message}"
            )
            mail.send(msg)
            print(f"✅ Email sent to: {app.config['MAIL_USERNAME']}")
        except Exception as e:
            print("❌ Email not sent:", e)

        return redirect("/thankyou")

    return render_template("contact.html")

@app.route('/admin/messages')
def view_messages():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT name, email, message FROM contacts ORDER BY id DESC")
    messages = c.fetchall()
    conn.close()
    return render_template("messages.html", messages=messages)

@app.route('/thankyou')
def thank_you():
    return "<h2>Thank you for contacting me!</h2>"

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)
