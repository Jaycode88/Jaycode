import pickle

# Load the token.pickle file
with open("token.pickle", "rb") as token_file:
    creds = pickle.load(token_file)

# Extract and print the refresh token
print("\n🔑 Your GMAIL_API_REFRESH_TOKEN:")
print(creds.refresh_token)

