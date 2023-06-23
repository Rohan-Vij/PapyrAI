import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from datetime import datetime

from dotenv import load_dotenv
import os


newline = "\n"


def paper_to_plaintext(paper):
    paper_str = f"""\
{paper["title"]}
{'-' * len(paper["title"])}
{paper["summary"]}

Links:
{newline.join(f' - {link["type"].upper()}: {link["link"]}' for link in paper["links"])}
Authors: {', '.join(paper['authors'])}
Published: {paper['published'].strftime('%B %Y')}"""

    if len(paper["keywords"]) > 0:
        paper_str += f"\nKeywords: {', '.join(paper['keywords'])}"

    return paper_str


def data_to_plaintext(data):
    return f"""\
Discover Custom Research Papers with Papyr AI
==============================================

Stay informed about the latest research in your field!

""" + "\n".join(
        paper_to_plaintext(paper) for paper in data
    )


def paper_to_html(paper):
    doi_link = next(link for link in paper["links"] if link["type"] == "doi")
    other_links = [link for link in paper["links"] if link["type"] != "doi"]

    return f"""\
      <div style="background-color: #ffffff; padding: 20px; margin-bottom: 20px; border-radius: 4px; box-shadow: 0 2px 5px rgba(0,0,0,0.1);">
        <!-- <img src="article1-thumbnail.jpg" alt="Article 1 Thumbnail" style="width: 100%; max-width: 300px; height: auto; margin-bottom: 10px;"> -->
        <a style="font-size: 20px; font-weight: bold; color: #3f51b5;" href="{doi_link["link"]}">{paper['title']}</a>
        <p style="font-size: 10px; font-weight: bold; margin-top: 5px; margin-bottom: 10px; color: #757575;" href="{paper['doi']}">Alternative Links: {" | ".join(f'<a style="color: #757575;" href="{link["link"]}">{link["type"]}</a>' for link in other_links)}</p>
        <p style="font-size: 16px; line-height: 1.5; color: #616161;">{paper['summary']}</p>
        <p style="font-size: 14px; margin-top: 10px; color: #757575;"><strong>Authors:</strong> {', '.join(paper['authors'])}</p>
        <p style="font-size: 14px; margin-top: 5px; color: #757575;"><strong>Published:</strong> {paper['published'].strftime('%B %Y')}</p>
        {f'<p style="font-size: 14px; margin-top: 5px; color: #757575;"><strong>Keywords:</strong> {", ".join(paper["keywords"])}</p>' if len(paper["keywords"]) > 0 else ""}
      </div>"""


def data_to_html(name, data):
    return f"""\
      <html>
      <body style="margin: 0; padding: 0; font-family: 'Roboto', Arial, sans-serif;">
      <div style="width: 100%; max-width: 600px; margin: 0 auto; background-color: #fafafa; padding: 20px; font-family: 'Roboto', Arial, sans-serif;">
        <div style="text-align: center; margin-bottom: 20px;">
          <h1 style="font-size: 24px; color: #3f51b5;">Discover Research Papers with Papyr AI</h1>
          <p style="font-size: 16px; color: #616161;">Stay informed about the latest research in your field!</p>
          <p style="font-size: 14px; color: #616161;">Weekly digest for {name}</p>
        </div>

        <div style="display: block; margin-bottom: 30px;">
          {newline.join(paper_to_html(paper) for paper in data)}
        </div>
      </div>
      </body>
      </html>
      """


def send_email(name, receiver_email, data):
    # loading env variables
    load_dotenv()

    sender_email = "papyrainewsletter@gmail.com"
    password = os.getenv("EMAIL_PASSWORD")

    message = MIMEMultipart("alternative")
    message[
        "Subject"
    ] = f"Your Weekly Papyr AI Newsletter - {datetime.today().strftime('%m-%d-%y')}"
    message["From"] = f"PapyrAI Newsletter {sender_email}"
    message["To"] = receiver_email

    # Create the plain-text and HTML version of your message
    text = data_to_plaintext(data)
    html = data_to_html(name, data)

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


# Call the function to send the email
# import json
# receiver_email = "rohankvij@gmail.com"  # Replace with the desired receiver email

# with open("tmp/arXiv_schema_clean.json", "r") as fin:
#     data = json.load(fin)
#     data["published"] = datetime.now()
#     send_email(receiver_email, [data])


# with open("tmp/arXiv_schema_clean.json", "r") as fin:
#     data = json.load(fin)
#     data["published"] = datetime.now()

# print(data_to_html([data]))
