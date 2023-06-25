import modules.api as api
import modules.mail as mail
import modules.gpt as gpt
from flask import Flask, render_template, request, url_for, redirect, session, g
from pymongo import MongoClient

from datetime import datetime
from dotenv import load_dotenv
import os

import xmltodict
import json
import requests

import random
import urllib.parse
import time

# Loading environment variables
load_dotenv()

# Retrieve the database password and secret key from environment variables
DB_PASSWORD = os.getenv('DB_PASSWORD')
SECRET_KEY = os.getenv('SECRET_KEY')

# Create the Flask application
app = Flask(__name__)
app.config["SECRET_KEY"] = SECRET_KEY

# MongoDB setup
# Connect to the MongoDB database using the provided password
client = MongoClient(f"mongodb+srv://main:{DB_PASSWORD}@cluster0.sae0tgt.mongodb.net/?retryWrites=true&w=majority")

# Access the "papyrai" database and "users" collection within it
db = client["papyrai"]
users = db["users"]

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
        return redirect(url_for("home"))

    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]
        topics = request.form["selected-topics"].split(",")

        if users.find_one({"email": email}):
            return render_template('signup.html', message="An account with that email address already exists.")
        else:
            users.insert_one({'name': name, 'email': email, 'password': password, 'topics': topics, 'activity': []})
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
        return redirect(url_for("home"))

    if request.method == "POST":
        email = request.form['email']
        password = request.form['pass']

        email_query = users.find_one({"email": email})
        if email_query:
            if password = email_query['password']:
                session['email'] = email
                return redirect(url_for("home"))
            else:
                return render_template("login.html", message="Incorrect password.")
        else:
            return render_template("login.html", message="An account with that email address does not exist.")

    return render_template("login.html")

@app.route('/api')
def use_api():
    """
    Handles API usage.

    This function retrieves papers based on the user's topics and generates recommendations using the GPT module.
    It then sends the recommendations via email.
    """
    user_info = users.find_one({"email": session["email"]})

    number_papers_to_get = 20
    papers_per_topic = 0
    topics = []

    # Divide the number of papers to get among the selected topics
    if len(user_info["topics"]) < 4:
        topics = user_info["topics"]
        papers_per_topic = number_papers_to_get // len(topics)
    else:
        # Randomly select four topics if the user has less than four
        topics = random.sample(user_info["topics"], 4)
        papers_per_topic = number_papers_to_get // 4

    # Retrieve the last five clicked topics
    # previously_clicked = user_info["activity"][-5:] if len(user_info["activity"]) > 5 else user_info["activity"]
    previously_clicked = user_info["activity"]

    print(previously_clicked)

    # Extract the topics from the previously clicked papers
    previous_topics = [activity_record["paper_topics"] for activity_record in previously_clicked]

    papers = []

    # Retrieve papers from arXiv API based on the selected topics
    for topic in topics:
        arXiv_api_response = requests.get(
            f"http://export.arxiv.org/api/query?search_query=all:{topic}&start=0&max_results={papers_per_topic//2}"
        )
        json_arXiv_api_response = xmltodict.parse(arXiv_api_response.text)
        entries = json_arXiv_api_response["feed"]["entry"]

        for arXiv_paper in entries:
            try:
                # Standardize the arXiv paper data
                arXiv_paper = api.standardize_arXiv(arXiv_paper)
            except:
                # Skip if the paper cannot be standardized
                continue
            arXiv_paper["keywords"] = [topic]
            papers.append(arXiv_paper)

    # Retrieve papers from Springer API based on the selected topics
        springer_api_key = os.getenv("springer_api_key")
        springer_api_response = requests.get(
            f"https://api.springernature.com/meta/v2/json?api_key={springer_api_key}&q=keyword%3A{topic}&s=1&p={papers_per_topic//2}"
        )

        records = springer_api_response.json()["records"]

        for springer_paper in records:
            try:
                # Standardize the Springer paper data
                springer_paper = api.standardize_springer(springer_paper)
            except:
                # Skip if the paper cannot be standardized
                continue
            springer_paper["keywords"] = [topic]
            papers.append(springer_paper)

    # Extract the titles of the retrieved papers
    titles = [paper["title"] for paper in papers]

    # Create an instance of the GPT module
    gpt_instance = gpt.GPTModule()

    try:
        # Generate recommendations using the GPT module
        recommendations = gpt_instance.recommend(titles, previous_topics)

        # Retrieve the recommended papers
        recommended_papers = [papers[int(index) - 1] for index in recommendations]
    except:
        # If GPT module fails or no recommendations are available, select a random subset of papers
        if len(papers) > 5:
            recommended_papers = random.sample(papers, 5)
        else:
            recommended_papers = papers

    # Summarize the recommended papers using the GPT module
    for paper in recommended_papers:
        summary = gpt_instance.summarize(paper["title"], paper["summary"])
        while summary == "Unable to fetch the response, Please try again.":
            summary = gpt_instance.summarize(paper["title"], paper["summary"])
            time.sleep(0.5)
            if summary != "Unable to fetch the response, Please try again.":
                break

        paper["summary"] = summary

        for link in paper["links"]:
            temp_link = link["link"]
            # Modify the link to include user-specific data for tracking purposes
            link["link"] = f"http://127.0.01:5000/c?email={user_info['email']}&paper_id={urllib.parse.quote(paper['doi'], safe='')}&paper_topics={paper['keywords'][0]}&link={urllib.parse.quote(temp_link, safe='')}"

    # Send the recommended papers via email
    mail.send_email(user_info["name"], user_info["email"], recommended_papers)

    return redirect(url_for("home"))

@app.route('/logout')
def logout():
    """
    Logs out the user by removing their email from the session.
    """
    session.pop("email", None)
    return redirect(url_for("index"))

@app.route('/home')
def home():
    """
    Renders the home page.

    If the user is not logged in, they are redirected to the login page.
    """
    if "email" not in session:
        return redirect(url_for("login"))

    return render_template("home.html")


@app.route('/c', methods=["GET"])
def clicked():
    """
    Handles link tracking.

    Example URL:
    https://127.0.01:5000/c?email=example@example.com&paper_id=123&paper_topics=topic1,topic2&link=example.com
    """
    email = request.args.get("email")
    paper_id = urllib.parse.unquote(request.args.get("paper_id"))
    paper_topics = request.args.get("paper_topics")
    redirect_url = urllib.parse.unquote(request.args.get("link"))

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

if __name__ == '__main__':
    app.run(debug=True, port=5678)
