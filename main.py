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
@app.route("/", methods=['post', 'get'])
def index():
    if "email" in session:
        return redirect(url_for("logged_in"))

    if request.method == "POST":
        name = request.form.get("fullname")
        email = request.form.get("email")
        password = request.form.get("password1")

        # if found in database showcase that it's found
        email_found = users.find_one({"email": email})

        if email_found:
            return render_template('index.html')

        else:
            # hash the password and encode it
            hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            # assing them in a dictionary in key value pairs
            user_input = {'name': name, 'email': email, 'password': hashed}
            # insert it in the record collection
            users.insert_one(user_input)

            # find the new created account and its email
            user_data = users.find_one({"email": email})
            new_email = user_data['email']

            # if registered redirect to logged in as the registered user
            return render_template('logged_in.html')
    return render_template('index.html')


@app.route("/login", methods=["POST", "GET"])
def login():
    if "email" in session:
        return redirect(url_for("logged_in"))

    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        # check if email exists in database
        email_found = users.find_one({"email": email})
        if email_found:
            email_val = email_found['email']
            passwordcheck = email_found['password']

            # encode the password and check if it matches
            if bcrypt.checkpw(password.encode('utf-8'), passwordcheck):
                session["email"] = email_val
                return redirect(url_for('logged_in'))
            else:
                if "email" in session:
                    return redirect(url_for("logged_in"))
                return render_template('login.html')
        else:
            return render_template('login.html')
    return render_template('login.html')


@app.route('/logged_in')
def logged_in():
    if "email" in session:
        email = session["email"]
        return render_template('logged_in.html', email=email)
    else:
        return redirect(url_for("login"))


@app.route("/logout", methods=["POST", "GET"])
def logout():
    if "email" in session:
        session.pop("email", None)
        return render_template("signout.html")
    else:
        return render_template('index.html')
