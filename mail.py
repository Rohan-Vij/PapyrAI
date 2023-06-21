import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from datetime import datetime

from dotenv import load_dotenv
import os


def data_to_plaintext(data):
    def paper_to_plaintext(paper):
        return f"""\
{paper["title"]}
{'-' * len(paper["title"])}
{paper["summary"]}

Authors: {', '.join(paper['authors'])}
Published: {paper['published'].strftime('%B %Y')}
Keywords: {', '.join(paper['keywords'])}"""

    return f"""\
Discover Custom Research Papers with Papyr AI
==============================================

Stay informed about the latest research in your field!

""" + "\n".join(
        paper_to_plaintext(paper) for paper in data
    )

def data_to_html(data):
    pass


def send_email(receiver_email):
    # loading env variables
    load_dotenv()

    sender_email = "papyrainewsletter@gmail.com"
    password = os.getenv("EMAIL_PASSWORD")

    message = MIMEMultipart("alternative")
    message[
        "Subject"
    ] = f"Your Weekly Papyr AI Newsletter - {datetime.today().strftime('%m-%d-%y')}"
    message["From"] = sender_email
    message["To"] = receiver_email

    # Create the plain-text and HTML version of your message
    text = """\
    Discover Custom Research Papers with Papyr AI
    ==============================================

    Stay informed about the latest research in your field!

    Example Research Paper 1
    ------------------------
    Explore groundbreaking findings in your research domain through this example research paper.

    Authors: John Doe, Jane Smith
    Published: June 2023
    Keywords: Artificial Intelligence, Machine Learning, Data Analysis

    Example Research Paper 2
    ------------------------
    Dive into cutting-edge findings with this hand-picked example research paper tailored to your interests.

    Authors: Sarah Johnson, Michael Brown
    Published: June 2023
    Keywords: Data Science, Natural Language Processing, Deep Learning
    """

    html = """\
    <html>
    <body style="margin: 0; padding: 0; font-family: 'Roboto', Arial, sans-serif;">
    <div style="width: 100%; max-width: 600px; margin: 0 auto; background-color: #fafafa; padding: 20px; font-family: 'Roboto', Arial, sans-serif;">
      <div style="text-align: center; margin-bottom: 20px;">
        <h1 style="font-size: 24px; color: #3f51b5;">Discover Research Papers with Papyr AI</h1>
        <p style="font-size: 16px; color: #616161;">Stay informed about the latest research in your field!</p>
      </div>

      <div style="display: block; margin-bottom: 30px;">
        <div style="background-color: #ffffff; padding: 20px; margin-bottom: 20px; border-radius: 4px; box-shadow: 0 2px 5px rgba(0,0,0,0.1);">
          <img src="article1-thumbnail.jpg" alt="Article 1 Thumbnail" style="width: 100%; max-width: 300px; height: auto; margin-bottom: 10px;">
          <h2 style="font-size: 20px; font-weight: bold; margin-bottom: 10px; color: #3f51b5;">Example Research Paper 1</h2>
          <p style="font-size: 16px; line-height: 1.5; color: #616161;">Explore groundbreaking findings in your research domain through this example research paper.</p>
          <p style="font-size: 14px; margin-top: 10px; color: #757575;"><strong>Authors:</strong> John Doe, Jane Smith</p>
          <p style="font-size: 14px; margin-top: 5px; color: #757575;"><strong>Published:</strong> June 2023</p>
          <p style="font-size: 14px; margin-top: 5px; color: #757575;"><strong>Keywords:</strong> Artificial Intelligence, Machine Learning, Data Analysis</p>
        </div>

        <div style="background-color: #ffffff; padding: 20px; border-radius: 4px; box-shadow: 0 2px 5px rgba(0,0,0,0.1);">
          <img src="article2-thumbnail.jpg" alt="Article 2 Thumbnail" style="width: 100%; max-width: 300px; height: auto; margin-bottom: 10px;">
          <h2 style="font-size: 20px; font-weight: bold; margin-bottom: 10px; color: #3f51b5;">Example Research Paper 2</h2>
          <p style="font-size: 16px; line-height: 1.5; color: #616161;">Dive into cutting-edge findings with this hand-picked example research paper tailored to your interests.</p>
          <p style="font-size: 14px; margin-top: 10px; color: #757575;"><strong>Authors:</strong> Sarah Johnson, Michael Brown</p>
          <p style="font-size: 14px; margin-top: 5px; color: #757575;"><strong>Published:</strong> June 2023</p>
          <p style="font-size: 14px; margin-top: 5px; color: #757575;"><strong>Keywords:</strong> Data Science, Natural Language Processing, Deep Learning</p>
        </div>
      </div>
    </div>
    </body>
    </html>
    """

    # Turn these into plain/html MIMEText objects
    part1 = MIMEText(text, "plain")
    part2 = MIMEText(html, "html")

    # Add HTML/plain-text parts to MIMEMultipart message
    # The email client will try to render the last part first
    message.attach(part1)
    message.attach(part2)

    # Create secure connection with server and send email
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, message.as_string())


# # Call the function to send the email
# receiver_email = "rohankvij@gmail.com"  # Replace with the desired receiver email
# send_email(receiver_email)

from api import standardize_arXiv
import requests, xmltodict, json


with open("tmp/arXiv_schema_clean.json", "r") as fin:
    data = json.load(fin)
    data["published"] = datetime.now()

print(data_to_plaintext([data]))
