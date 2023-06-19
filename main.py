from flask import Flask, render_template, request, url_for, redirect, session
from pymongo import MongoClient
import bcrypt

from dotenv import load_dotenv
import os


# loading env variables
load_dotenv()

DB_PASSWORD = os.getenv('DB_PASSWORD')
SECRET_KEY = os.getenv('SECRET_KEY')

# create app
app = Flask(__name__)
app.config["SECRET_KEY"] = SECRET_KEY

# mongodb setup
client = MongoClient(
    f"mongodb+srv://main:{DB_PASSWORD}@cluster0.sae0tgt.mongodb.net/?retryWrites=true&w=majority")

db = client["papyrai"]
users = db["users"]

# user management
@app.route('/signup', methods=["GET", "POST"])
def signup():
    if "email" in session:
        return redirect(url_for("logged_in"))

    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]

        if users.find_one({"email": email}):
            return render_template('index.html', message="An account with that email address already exists.")

        else:
            hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            users.insert_one({'name': name, 'email': email, 'password': hashed})
            session['email'] = email
            
            return redirect(url_for("home"))
    return render_template('index.html')


@app.route('/login', methods=["GET", "POST"])
def login():
    if "email" in session:
        return redirect(url_for("logged_in"))

    if request.method == "POST":
        email = request.form['email']
        password = request.form['pass']

        # Make sure that account does exist
        email_query = users.find_one({"email": email})
        if email_query:
            if bcrypt.checkpw(password.encode('utf-8'), email_query['password']):
                session['email'] = email
                return redirect(url_for("home"))
            else:
                return render_template("login.html", message="Incorrect password.")
        else:
            return render_template("login.html", message="An account with that email address does not exist.")
    return render_template("login.html")


@app.route('/home')
def home():
    if "email" in session:
        return render_template('home.html')
    else:
        return redirect(url_for("login"))


@app.route("/logout")
def logout():
    if "email" in session:
        session.pop("email", None)
        return render_template("signout.html")
    else:
        return render_template('index.html')

@app.before_request
def before_request():
    g.user = None
    if "user" in session:
        g.user = session['user']