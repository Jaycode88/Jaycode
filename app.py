from flask import Flask, render_template, request, jsonify
import os
from dotenv import load_dotenv
import base64
from email.message import EmailMessage
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
import pickle
import requests


# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")

# Gmail API configuration
SCOPES = ["https://www.googleapis.com/auth/gmail.send"]
CREDENTIALS_FILE = "credentials.json"
TOKEN_FILE = "token.pickle"


def authenticate_gmail_api():
    creds = None
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, "rb") as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            from google_auth_oauthlib.flow import InstalledAppFlow
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_FILE, "wb") as token:
            pickle.dump(creds, token)

    return build("gmail", "v1", credentials=creds)


def send_email_gmail(name, email, message):
    try:
        service = authenticate_gmail_api()
        msg = EmailMessage()
        msg["Subject"] = f"New Contact Form Submission from {name}"
        msg["From"] = email
        msg["To"] = os.getenv("RECIPIENT_EMAIL")
        msg.set_content(
            f"Name: {name}\n"
            f"Email: {email}\n"
            f"Message:\n{message}"
        )
        raw_message = base64.urlsafe_b64encode(msg.as_bytes()).decode()
        service.users().messages().send(userId="me", body={"raw": raw_message}).execute()
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        message = request.form.get("message")
        honeypot = request.form.get("honeypot")

        if not name or not email or not message:
            return jsonify({"status": "error", "message": "Please fill out all required fields."})
        
        # Reject if the honeypot is filled (bot detected)
        if honeypot:
            return jsonify({"status": "error", "message": "Spam detected. Submission blocked."})

        # Verify reCAPTCHA response
        recaptcha_secret = os.getenv("RECAPTCHA_SECRET_KEY")  # Load secret key from .env
        recaptcha_verify_url = "https://www.google.com/recaptcha/api/siteverify"
        recaptcha_data = {"secret": recaptcha_secret, "response": recaptcha_response}
        recaptcha_response = requests.post(recaptcha_verify_url, data=recaptcha_data).json()

        if not recaptcha_response.get("success"):
            return jsonify({"status": "error", "message": "reCAPTCHA verification failed. Please try again."})

        if send_email_gmail(name, email, message):
            return jsonify({"status": "success", "message": "Your message has been sent successfully!"})
        else:
            return jsonify({"status": "error", "message": "Failed to send your message. Please try again later."})

    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True)
