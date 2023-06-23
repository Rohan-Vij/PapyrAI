from flask import Flask, render_template, request, url_for, redirect, session, g
from pymongo import MongoClient
import bcrypt

from datetime import datetime
from dotenv import load_dotenv
import os

import xmltodict
import json
import requests

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

# Routes

@app.route('/')
def index():
    """
    Renders the index page.

    """

    return render_template('index.html')


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
        topics = request.form["selected-topics"].split(",")

        print(topics)

        if users.find_one({"email": email}):
            return render_template('signup.html', message="An account with that email address already exists.")
        else:
            hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            users.insert_one(
                {'name': name, 'email': email, 'password': hashed, 'topics': topics, 'activity': []})
            session['email'] = email

            return redirect(url_for("home"))

    return render_template('signup.html')


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

import api

@app.route('/api')
def use_api():
    arXiv_api_response = requests.get(
      "http://export.arxiv.org/api/query?search_query=all:electron"
    )
    json_arXiv_api_response = xmltodict.parse(arXiv_api_response.text)
    entries = json_arXiv_api_response["feed"]["entry"]
    print(json.dumps(api.standardize_arXiv(entries[0]), indent=4, default=str))

    springer_api_key = os.getenv("springer_api_key")
    springer_api_response = requests.get(
        f"https://api.springernature.com/meta/v2/json?api_key={springer_api_key}&q=keyword%3Aelectron&s=1&p=10"
    )

    records = springer_api_response.json()["records"]
    print(json.dumps(api.standardize_springer(records[0]), indent=4, default=str))

    

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
    
# Link tracking

@app.route('/c', methods=["GET"])
def clicked():
    """
    Handles link tracking.

    Example URL:
    https://127.0.01:5000/c?email=example@example.com&paper_id=123&paper_topics=topic1,topic2&redirect=example.com
    """
    email = request.args.get("email")
    paper_id = request.args.get("paper_id")
    paper_topics = request.args.get("paper_topics")
    redirect_url = request.args.get("redirect")

    click_object = {
        "email": email,
        "paper_id": paper_id,
        "paper_topics": paper_topics,
        "date": datetime.now()
    }

    users.update_one({"email": email}, {"$push": {"activity": click_object}})

    return redirect(redirect_url)


@app.before_request
def before_request():
    """
    Global function executed before each request.

    It sets the 'g.email' variable to the user's email if they are logged in.
    """
    g.email = None
    if "email" in session:
        g.email = session['email']


# Run the Flask application
if __name__ == '__main__':
    app.run(debug=True)
