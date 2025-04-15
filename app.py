from werkzeug.security import generate_password_hash, check_password_hash
from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
import os
from dotenv import load_dotenv
import base64
from email.message import EmailMessage
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
import pickle
import requests
import json
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

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
        name = request.form.get("name")
        email = request.form.get("email")
        project_type = request.form.get("project_type")
        message = request.form.get("message")
        honeypot = request.form.get("honeypot")
        recaptcha_response = request.form.get("g-recaptcha-response")

        if not name or not email or not message:
            return jsonify({"status": "error", "message": "Please fill out all required fields."})
        if honeypot:
            return jsonify({"status": "error", "message": "Spam detected. Submission blocked."})
        if not recaptcha_response or not verify_recaptcha(recaptcha_response):
            return jsonify({"status": "error", "message": "reCAPTCHA verification failed. Please try again."})

        if send_email_gmail(name, email, project_type, message):
            return jsonify({"status": "success", "message": "Your message has been sent successfully!"})
        else:
            return jsonify({"status": "error", "message": "Failed to send your message. Please try again later."})
    return render_template("index.html")


@app.route("/free-review", methods=["GET", "POST"])
def free_review():
    if request.method == "POST":
        first_name = request.form.get("first_name")
        last_name = request.form.get("last_name")
        email = request.form.get("email")
        website_url = request.form.get("website_url")

        # Get current reset point
        counter = WeeklyCounter.query.first()
        reset_time = counter.reset_time if counter else datetime.min

        # Count reviews submitted since reset
        weekly_count = ReviewRequest.query.filter(ReviewRequest.submitted_at >= reset_time).count()
        if weekly_count >= 5:
            return jsonify({
                "status": "error",
                "message": "The request queue is full for this week. Please try again next week or contact us directly."
            })

        if website_url and not website_url.startswith(("http://", "https://")):
            website_url = "https://" + website_url

        honeypot = request.form.get("honeypot")
        recaptcha_response = request.form.get("g-recaptcha-response")
        if honeypot:
            return jsonify({"status": "error", "message": "Spam detected. Submission blocked."})
        if not recaptcha_response or not verify_recaptcha(recaptcha_response):
            return jsonify({"status": "error", "message": "reCAPTCHA verification failed."})

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
        send_confirmation_email(email, first_name)
        return jsonify({"status": "success", "message": "Your review request has been submitted!"})
    return render_template("free_review.html")


@app.route("/admin/dashboard")
def admin_dashboard():
    if not session.get("admin_logged_in"):
        flash("Please log in to access the admin dashboard.", "error")
        return redirect(url_for("admin_login"))

    counter = WeeklyCounter.query.first()
    reset_time = counter.reset_time if counter else datetime.min
    weekly_count = ReviewRequest.query.filter(ReviewRequest.submitted_at >= reset_time).count()
    requests = ReviewRequest.query.order_by(ReviewRequest.submitted_at.desc()).all()
    return render_template("admin_dashboard.html", requests=requests, weekly_count=weekly_count)


@app.route("/admin/reset-weekly-limit", methods=["POST"])
def reset_weekly_limit():
    if not session.get("admin_logged_in"):
        flash("Access denied.", "error")
        return redirect(url_for("admin_login"))

    counter = WeeklyCounter.query.first()
    if not counter:
        counter = WeeklyCounter(reset_time=datetime.utcnow())
        db.session.add(counter)
    else:
        counter.reset_time = datetime.utcnow()
    db.session.commit()
    flash("Weekly review counter has been reset.", "success")
    return redirect(url_for("admin_dashboard"))


@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        user = AdminUser.query.filter_by(username=username).first()
        if user and check_password_hash(user.password_hash, password):
            session["admin_logged_in"] = True
            return redirect(url_for("admin_dashboard"))
        else:
            return render_template("admin_login.html", error="Invalid credentials.")
    return render_template("admin_login.html")


@app.route("/admin/logout")
def admin_logout():
    session.pop("admin_logged_in", None)
    return redirect(url_for("admin_login"))


@app.route("/admin/update", methods=["POST"])
def update_review():
    if not session.get("admin_logged_in"):
        flash("Access denied.", "error")
        return redirect(url_for("admin_login"))

    save_id = request.form.get("save_id")
    if save_id:
        request_to_update = ReviewRequest.query.get(int(save_id))
        if request_to_update:
            new_status = request.form.get(f"status_{save_id}")
            new_notes = request.form.get(f"notes_{save_id}")
            request_to_update.status = new_status
            request_to_update.notes = new_notes
            db.session.commit()
            flash(f"Review ID {save_id} updated.", "success")

    return redirect(url_for("admin_dashboard"))


@app.route("/admin/delete", methods=["POST"])
def delete_review():
    if not session.get("admin_logged_in"):
        flash("Access denied.", "error")
        return redirect(url_for("admin_login"))

    delete_id = request.form.get("delete_id")
    if delete_id:
        review = ReviewRequest.query.get(int(delete_id))
        if review:
            db.session.delete(review)
            db.session.commit()
            flash(f"Review ID {delete_id} deleted.", "success")

    return redirect(url_for("admin_dashboard"))


def send_confirmation_email(to_email, first_name):
    subject = "Your Website Review Request Has Been Received"
    sender_email = os.getenv("SMTP_USERNAME")
    smtp_server = os.getenv("SMTP_SERVER")
    smtp_port = int(os.getenv("SMTP_PORT"))
    smtp_username = os.getenv("SMTP_USERNAME")
    smtp_password = os.getenv("SMTP_PASSWORD")

    text = f"""
Hi {first_name},

Thank you for requesting a free website review from JayCode!
We'll send your report within 2 business days.

Best regards,  
Joe – JayCode.co.uk
"""

    html = f"""
<html>
  <body>
    <p>Hi {first_name},</p>
    <p>Thank you for requesting a <strong>free website review</strong> from <strong>JayCode</strong>!</p>
    <p>We'll send your report within <strong>2 business days</strong>.</p>
    <p>Best,<br>Joe<br><strong>JayCode.co.uk</strong></p>
  </body>
</html>
"""

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = sender_email
    msg["To"] = to_email
    msg.attach(MIMEText(text, "plain"))
    msg.attach(MIMEText(html, "html"))

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_username, smtp_password)
            server.send_message(msg)
        print(f"✅ Confirmation email sent to {to_email}")
    except Exception as e:
        print(f"❌ Failed to send confirmation email: {e}")


class ReviewRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    email = db.Column(db.String(150))
    website_url = db.Column(db.String(300))
    status = db.Column(db.String(50), default='requested')
    notes = db.Column(db.Text, nullable=True)
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)


class AdminUser(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class WeeklyCounter(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    reset_time = db.Column(db.DateTime, default=datetime.utcnow)


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
