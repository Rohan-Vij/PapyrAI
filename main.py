from flask import Flask, render_template, request, url_for, redirect, session, g
from pymongo import MongoClient
import bcrypt

from dotenv import load_dotenv
import os

# loading env variables
load_dotenv()

# Retrieve the database password and secret key from environment variables
DB_PASSWORD = os.getenv('DB_PASSWORD')
SECRET_KEY = os.getenv('SECRET_KEY')

# Create the Flask application
app = Flask(__name__)
app.config["SECRET_KEY"] = SECRET_KEY

# MongoDB setup
# Connect to the MongoDB database using the provided password
client = MongoClient(
    f"mongodb+srv://main:{DB_PASSWORD}@cluster0.sae0tgt.mongodb.net/?retryWrites=true&w=majority")

# Access the "papyrai" database and "users" collection within it
db = client["papyrai"]
users = db["users"]

# User management routes


@app.route('/signup', methods=["GET", "POST"])
def signup():
    """
    Handles user signup.

    If the user is already logged in, they are redirected to the home page.
    If the request method is POST, it registers a new user with the provided information.
    """
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
            users.insert_one(
                {'name': name, 'email': email, 'password': hashed})
            session['email'] = email

            return redirect(url_for("home"))

    return render_template('index.html')


@app.route('/login', methods=["GET", "POST"])
def login():
    """
    Handles user login.

    If the user is already logged in, they are redirected to the home page.
    If the request method is POST, it verifies the user's credentials and logs them in.
    """
    if "email" in session:
        return redirect(url_for("logged_in"))

    if request.method == "POST":
        email = request.form['email']
        password = request.form['pass']

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
    """
    Renders the home page.

    If the user is logged in, the home page is rendered.
    Otherwise, the user is redirected to the login page.
    """
    if "email" in session:
        return render_template('home.html')
    else:
        return redirect(url_for("login"))


@app.route("/logout")
def logout():
    """
    Logs out the user.

    If the user is logged in, their session is terminated, and they are redirected to the signout page.
    If the user is not logged in, they are redirected to the index page.
    """
    if "email" in session:
        session.pop("email", None)
        return render_template("signout.html")
    else:
        return render_template('index.html')


@app.before_request
def before_request():
    """
    Global function executed before each request.

    It sets the 'g.email' variable to the user's email if they are logged in.
    """
    g.email = None
    if "email" in session:
        g.email = session['email']
