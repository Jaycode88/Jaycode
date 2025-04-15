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
import json
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
 


# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///reviews.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


# Gmail API configuration
SCOPES = ["https://www.googleapis.com/auth/gmail.send"]
CREDENTIALS_FILE = "credentials.json"
TOKEN_FILE = "token.pickle"

# Google reCAPTCHA Secret Key (from .env)
RECAPTCHA_SECRET_KEY = os.getenv("RECAPTCHA_SECRET_KEY")

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


def verify_recaptcha(recaptcha_response):
    """ Verify reCAPTCHA response with Google """
    print("🔍 Verifying reCAPTCHA...")
    url = "https://www.google.com/recaptcha/api/siteverify"
    data = {
        "secret": RECAPTCHA_SECRET_KEY,
        "response": recaptcha_response
    }
    response = requests.post(url, data=data)
    result = response.json()

    return result.get("success", False)


def send_email_gmail(name, email, project_type, message):
    try:
        service = authenticate_gmail_api()
        msg = EmailMessage()
        msg["Subject"] = f"New Contact Form Submission from {name}"
        msg["From"] = email
        msg["To"] = os.getenv("RECIPIENT_EMAIL")
        msg.set_content(
            f"Name: {name}\n"
            f"Email: {email}\n"
            f"Project Type: {project_type}\n\n"
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
        print("\n🔹 [DEBUG] New POST request received!")  # Confirming a POST request

        name = request.form.get("name")
        email = request.form.get("email")
        project_type = request.form.get("project_type")
        message = request.form.get("message")
        honeypot = request.form.get("honeypot")
        recaptcha_response = request.form.get("g-recaptcha-response")

        print(f"📩 Received Form Data - Name: {name}, Email: {email}, Message: {message[:30]}...")
        print(f"🕵️‍♂️ Honeypot Field: {request.form.get('honeypot')}") 

        if not name or not email or not message:
            return jsonify({"status": "error", "message": "Please fill out all required fields."})

        # Reject if the honeypot is filled (bot detected)
        if honeypot:
            print("🚨 [BOT DETECTED] Honeypot field was filled! Blocking submission.")
            return jsonify({"status": "error", "message": "Spam detected. Submission blocked."})
        
        # Validate reCAPTCHA
        if not recaptcha_response or not verify_recaptcha(recaptcha_response):
            print("❌ reCAPTCHA verification failed!")
            return jsonify({"status": "error", "message": "reCAPTCHA verification failed. Please try again."})
        print("✅ reCAPTCHA verified successfully!")
        

        if send_email_gmail(name, email, project_type, message):
            print("📨 Email sent successfully!")
            return jsonify({"status": "success", "message": "Your message has been sent successfully!"})
        else:
            print("❌ Failed to send email!")
            return jsonify({"status": "error", "message": "Failed to send your message. Please try again later."})

    return render_template("index.html")


@app.route("/privacy")
def privacy():
    return render_template("privacy.html")


@app.route("/terms")
def terms():
    return render_template("terms.html")


@app.route("/oauth2callback")
def oauth2callback():
    return "OAuth2 callback successful!", 200


@app.route("/free-review", methods=["GET", "POST"])
def free_review():
    if request.method == "POST":
        first_name = request.form.get("first_name")
        last_name = request.form.get("last_name")
        email = request.form.get("email")
        website_url = request.form.get("website_url")
        # Normalize the website URL if it doesn't start with http:// or https://
        if website_url and not website_url.startswith(("http://", "https://")):
            website_url = "https://" + website_url

        honeypot = request.form.get("honeypot")
        recaptcha_response = request.form.get("g-recaptcha-response")

        if honeypot:
            print("🚫 Honeypot triggered! Possible spam.")
            return jsonify({"status": "error", "message": "Spam detected. Submission blocked."})

        if not recaptcha_response or not verify_recaptcha(recaptcha_response):
            print("❌ reCAPTCHA failed.")
            return jsonify({"status": "error", "message": "reCAPTCHA verification failed."})
        
        # Check for duplicates
        existing = ReviewRequest.query.filter(
            (ReviewRequest.email == email) | (ReviewRequest.website_url == website_url)
        ).first()

        if existing:
            return jsonify({
                "status": "error",
                "message": "This email or website has already been submitted for review."
            })

        new_request = ReviewRequest(
            first_name=first_name,
            last_name=last_name,
            email=email,
            website_url=website_url
        )
        db.session.add(new_request)
        db.session.commit()

        send_email_gmail(
            name=f"{first_name} {last_name}",
            email=email,
            project_type="Free Website Review",
            message=f"New review request for: {website_url}"
        )

        return jsonify({"status": "success", "message": "Your review request has been submitted!"})

    return render_template("free_review.html")


@app.route("/free-review/terms")
def free_review_terms():
    return render_template("free-review-terms.html")


@app.route("/free-review/privacy")
def free_review_privacy():
    return render_template("free-review-privacy.html")

class ReviewRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    email = db.Column(db.String(150))
    website_url = db.Column(db.String(300))
    status = db.Column(db.String(50), default='requested')  # requested, in_progress, completed
    notes = db.Column(db.Text, nullable=True)
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)




if __name__ == "__main__":
    app.run(debug=True)
