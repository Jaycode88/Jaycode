from google_auth_oauthlib.flow import InstalledAppFlow
import pickle

SCOPES = ["https://www.googleapis.com/auth/gmail.send"]
CREDENTIALS_FILE = "credentials.json"
REDIRECT_URI = "https://jaycode.co.uk/oauth2callback"  # Must match your Google Cloud OAuth settings!

def main():
    flow = InstalledAppFlow.from_client_secrets_file(
        CREDENTIALS_FILE, SCOPES, redirect_uri=REDIRECT_URI
    )

    # Generate the authorization URL
    auth_url, _ = flow.authorization_url(prompt="consent", access_type="offline")

    print("\n🔗 Open this link in your local browser and authorize the app:")
    print(auth_url)

    # Get the authorization code from the user
    auth_code = input("\n📋 Paste the authorization code here: ").strip()

    # Fetch token using the code
    flow.fetch_token(code=auth_code)
    creds = flow.credentials

    # Save token
    with open("token.pickle", "wb") as token_file:
        pickle.dump(creds, token_file)

    print("\n✅ Token generated and saved successfully!")

if __name__ == "__main__":
    main()

