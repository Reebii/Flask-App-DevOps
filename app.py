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
app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_USERNAME')

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

        # Send Email Notification to Admin
        try:
            msg = Message(
                subject="📩 New Contact Submission",
                recipients=[app.config['MAIL_USERNAME']],
                body=f"New message from:\n\nName: {name}\nEmail: {email}\n\nMessage:\n{message}"
            )
            mail.send(msg)
            print(f"✅ Admin email sent to: {app.config['MAIL_USERNAME']}")
        except Exception as e:
            print("❌ Admin email not sent:", e)

        # Auto-reply to User
        try:
            user_msg = Message(
                subject="✅ We received your message!",
                recipients=[email],
                body=f"Hi {name},\n\nThanks for contacting us! We'll get back to you shortly.\n\nYour message:\n{message}\n\nBest regards,\nYour Website Team"
            )
            mail.send(user_msg)
            print(f"📬 Auto-reply sent to: {email}")
        except Exception as e:
            print("❌ Auto-reply failed:", e)

        return redirect("/thankyou")

    return render_template("contact.html")

@app.route('/thankyou')
def thank_you():
    return render_template("thankyou.html")


if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)
