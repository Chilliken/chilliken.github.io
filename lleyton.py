import csv
import os
from flask import Flask, render_template, request, redirect, session

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "fallback_secret_key")  # Uses environment variable

login_data = []  # Stores user login details

# Load login data from file
try:
    with open('logindata.txt', 'r') as f:
        reader = csv.DictReader(f)
        for record in reader:
            login_data.append(dict(record))  # Ensure dict format
except FileNotFoundError:
    print("Warning: logindata.txt not found. Starting with an empty user list.")

@app.route("/")
def index():
    return render_template("index.html", username=session.get("username"))

@app.route("/register", methods=["GET", "POST"])
def register():
    msg = ''
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        # Check if username already exists
        for rec in login_data:
            if rec["username"] == username:
                return render_template('register.html', msg=[username, "Username already taken"])

        # Add new user
        new_user = {"username": username, "password": password}
        login_data.append(new_user)

        # Save user to file
        write_to_file(username, password)

        msg = [username, "Success"]

    return render_template('register.html', msg=msg)

@app.route("/login", methods=["GET", "POST"])
def login():
    msg = ''
    if request.method == "POST":
        username, password = request.form["username"], request.form["password"]

        if authenticate(username, password):
            session['username'] = username  # Do not store passwords!
            return redirect("/profile")
        else:
            msg =[username, "Failure"]
            
    return render_template('login.html', msg=msg)

@app.route("/profile")
def profile():
    if "username" not in session:
        return redirect("/login")
    return render_template("profile.html", username=session["username"])

@app.route("/logout")
def logout():
    session.pop("username", None)
    return redirect("/login")

@app.route("/admin")
def admin():
    return "<br>".join([f"Username: {user['username']}, Password: {user['password']}" for user in login_data])

@app.route('/logindata')
def logindata():
    return render_template('logindata.html', data=student_details)

def write_to_file(username, password):
    """Appends a new user record to logindata.txt"""
    with open('logindata.txt', 'a', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=["username", "password"])
        writer.writerow({"username": username, "password": password})  # Append new user

def authenticate(username, password):
    for user in login_data:
        if user["username"] == username and user["password"] == password:
            return True
    return False

if __name__ == "__main__":
    app.run()
