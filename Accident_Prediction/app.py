import sqlite3
from flask import Flask, render_template, request, redirect, session

app = Flask(__name__)
app.secret_key = "supersecretkey"

# ================= DATABASE SETUP ================= #

def init_db():
    conn = sqlite3.connect('accident.db')
    cursor = conn.cursor()

    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            email TEXT UNIQUE,
            password TEXT,
            role TEXT
        )
    ''')

    # Accident prediction table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS accident_predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            rural_urban TEXT,
            cause TEXT,
            road_feature TEXT,
            road_condition TEXT,
            weather_condition TEXT,
            vehicle_responsible TEXT,
            predicted_severity TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    conn.commit()
    conn.close()

init_db()

# ================= HOME ================= #

@app.route("/")
def home():
    return render_template("index.html")

# ================= USER MODULE ================= #

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]

        conn = sqlite3.connect("accident.db")
        cursor = conn.cursor()

        try:
            cursor.execute(
                "INSERT INTO users (name, email, password, role) VALUES (?, ?, ?, ?)",
                (name, email, password, "user")
            )
            conn.commit()
            conn.close()
            return redirect("/user_login")
        except:
            conn.close()
            return "Email already exists!"

    return render_template("register.html")

@app.route("/user_login", methods=["GET", "POST"])
def user_login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        conn = sqlite3.connect("accident.db")
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM users WHERE email=? AND password=? AND role='user'",
            (email, password)
        )

        user = cursor.fetchone()
        conn.close()

        if user:
            session["user_id"] = user[0]
            session["user_name"] = user[1]
            return redirect("/user_dashboard")
        else:
            return "Invalid credentials!"

    return render_template("user_login.html")

@app.route("/user_dashboard")
def user_dashboard():
    if "user_id" not in session:
        return redirect("/user_login")

    return render_template("dashboard.html", name=session["user_name"])

# ================= ADMIN MODULE ================= #

@app.route("/admin_login", methods=["GET", "POST"])
def admin_login():

    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        # Hardcoded Admin
        if email == "admin@gmail.com" and password == "admin123":
            session["admin"] = True
            return redirect("/admin_dashboard")
        else:
            return "Invalid Admin Credentials!"

    return render_template("admin_login.html")

@app.route("/admin_dashboard")
def admin_dashboard():
    if "admin" not in session:
        return redirect("/admin_login")

    return render_template("admin_dashboard.html")

# ================= LOGOUT ================= #

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

# ================= RUN SERVER ================= #

if __name__ == "__main__":
    app.run(debug=True)