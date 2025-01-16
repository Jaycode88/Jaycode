from flask import Flask, render_template, request, flash, redirect, url_for
import os
from dotenv import load_dotenv
import base64
from email.message import EmailMessage
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
import pickle
import logging

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,  # Set to DEBUG for development or INFO for production
    format="%(asctime)s - %(levelname)s - %(message)s",
)

# Gmail API configuration
SCOPES = ["https://www.googleapis.com/auth/gmail.send"]
CREDENTIALS_FILE = "credentials.json"
TOKEN_FILE = "token.pickle"


def authenticate_gmail_api():
    """
    Authenticate with the Gmail API and return the service object.
    """
    creds = None
    # Load saved token if it exists
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, "rb") as token:
            creds = pickle.load(token)

    # If there are no valid credentials, authenticate the user
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            from google_auth_oauthlib.flow import InstalledAppFlow
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)

        # Save the credentials for future use
        with open(TOKEN_FILE, "wb") as token:
            pickle.dump(creds, token)

    return build("gmail", "v1", credentials=creds)


def send_email_gmail(name, email, message, newsletter):
    """
    Send an email using the Gmail API.
    """
    try:
        service = authenticate_gmail_api()

        # Create the email message
        msg = EmailMessage()
        msg["Subject"] = f"New Contact Form Submission from {name}"
        msg["From"] = email
        msg["To"] = "joeseabrook0306@gmail.com"
        newsletter_status = "Yes" if newsletter else "No"
        msg.set_content(
            f"Name: {name}\n"
            f"Email: {email}\n"
            f"Newsletter Subscription: {newsletter_status}\n\n"
            f"Message:\n{message}"
        )

        # Encode the message in base64
        raw_message = base64.urlsafe_b64encode(msg.as_bytes()).decode()

        # Send the email
        send_message = (
            service.users()
            .messages()
            .send(userId="me", body={"raw": raw_message})
            .execute()
        )

        logging.info(f"Email sent successfully! Message ID: {send_message['id']}")
        return True
    except Exception as e:
        logging.error(f"Error sending email: {e}")
        return False


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        # Capture form data
        name = request.form.get("name")
        email = request.form.get("email")
        message = request.form.get("message")
        newsletter = request.form.get("newsletter") == "on"  # True if checkbox is checked

        # Basic validation
        if not name or not email or not message:
            flash("Please fill out all required fields.", "error")
            return redirect(url_for("index"))

        # Send email
        if send_email_gmail(name, email, message, newsletter):
            flash("Your message has been sent successfully!", "success")
        else:
            flash("Failed to send your message. Please try again later.", "error")

        return redirect(url_for("index"))

    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True)
