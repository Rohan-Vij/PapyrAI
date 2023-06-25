

from pymongo import MongoClient

from datetime import datetime
from dotenv import load_dotenv

import sys
import os

# Get the parent directory path
parent_dir = os.path.dirname(os.path.abspath(__file__))
parent_parent_dir = os.path.dirname(parent_dir)

# Add the parent directory to sys.path
sys.path.append(parent_parent_dir)

# Import the modules
import modules.api as api
import modules.mail as mail
import modules.gpt as gpt

# Remove the parent directory from sys.path (optional)
sys.path.remove(parent_parent_dir)

import xmltodict
import requests

import random
import urllib.parse
import time

# Basic logging setup

import logging
logging.basicConfig(filename='weekly_job/app.log', encoding='utf-8', level=logging.INFO)

# Loading environment variables
load_dotenv()

# Retrieve the database password and secret key from environment variables
DB_PASSWORD = os.getenv('DB_PASSWORD')


# MongoDB setup
# Connect to the MongoDB database using the provided password
client = MongoClient(f"mongodb+srv://main:{DB_PASSWORD}@cluster0.sae0tgt.mongodb.net/?retryWrites=true&w=majority")

# Access the "papyrai" database and "users" collection within it
db = client["papyrai"]
users = db["users"]

all_users = users.find({})

def send_newsletter(user_info):
    """
    This function retrieves papers based on the user's topics and generates recommendations using the GPT module.
    It then sends the recommendations via email.
    """
    try:
        # user_info = users.find_one({"email": session["email"]})

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
        previously_clicked = user_info["activity"][-5:] if len(user_info["activity"]) > 5 else user_info["activity"]
        # previously_clicked = user_info["activity"]

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
            attempts = 0
            while summary == "Unable to fetch the response, Please try again.":
                if attempts == 20:
                    raise TimeoutError
                summary = gpt_instance.summarize(paper["title"], paper["summary"])
                time.sleep(0.5)
                attempts += 1
                if summary != "Unable to fetch the response, Please try again.":
                    break

            paper["summary"] = summary

            for link in paper["links"]:
                temp_link = link["link"]
                # Modify the link to include user-specific data for tracking purposes
                link["link"] = f"http://127.0.01:5000/c?email={user_info['email']}&paper_id={urllib.parse.quote(paper['doi'], safe='')}&paper_topics={paper['keywords'][0]}&link={urllib.parse.quote(temp_link, safe='')}"

        # Send the recommended papers via email
        mail.send_email(user_info["name"], user_info["email"], recommended_papers)
    except Exception:
        return f"Error:\n{traceback.format_exc()}"
    else:
        return "Success"
    

for user in all_users:
    result = send_newsletter(user)
    if result.startswith("Error"):
        print("error")
        logging.error(f"{user['email']} @ {datetime.now()} - {result}")
    else:
        print("success")
        logging.info(f"{user['email']} @ {datetime.now()} - {result}")