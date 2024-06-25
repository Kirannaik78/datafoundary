import os.path
import datetime

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from models.emailModels import Email, SessionLocal

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

# paths to token and credentials json files
TOKEN_PATH = os.path.join(os.path.dirname(__file__), "../token.json")
CREDENTIALS_PATH = os.path.join(os.path.dirname(__file__), '../credentials.json')


def authenticate_gmail():
    """authenticate with gmail api using oauth2 credentials."""
    creds = None

    # check if token file exists and load credentials from it
    if os.path.exists(TOKEN_PATH):
        creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)

    # if credentials are not valid, refrsh them
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # create oauth flow to authorize user and obtain new credentials
            flow = InstalledAppFlow.from_client_secrets_file(
                CREDENTIALS_PATH, SCOPES
            )
            # Run local server to get authorization
            creds = flow.run_local_server(port=0)

        # Save the credentials to token file for future use
        with open(TOKEN_PATH, "w") as token:
            token.write(creds.to_json())

    # Build and return the Gmail service using obtained credentials
    service = build("gmail", "v1", credentials=creds)
    return service


def fetch_emails():
    """Fetch emails from Gmail and store them in the database."""

    service = authenticate_gmail()
    results = service.users().messages().list(userId='me', maxResults=10).execute()
    messages = results.get('messages', [])  # extract message from api response

    db = SessionLocal()

    # iterate through each message and process its details
    for message in messages:
        msg = service.users().messages().get(userId='me', id=message['id']).execute()
        payload = msg['payload']
        headers = payload['headers']

        # Extract email details from message headers
        from_email = next(header['value'] for header in headers if header['name'] == 'From')
        subject = next(header['value'] for header in headers if header['name'] == 'Subject')
        body = ""
        if 'data' in payload['body']:
            body = payload['body']['data']

        # Extract email body content if available
        received_datetime = datetime.datetime.fromtimestamp(int(msg['internalDate']) / 1000)
        print(received_datetime)

        # Create Email object with extracted details
        email = Email(
            id=message['id'],
            from_email=from_email,
            subject=subject,
            body=body,
            received_datetime=received_datetime
        )
        # Merge (upsert) the Email object into the database session
        db.merge(email)

    db.commit()  # Commit changes to the database
    db.close()  # Close the database session


if __name__ == "__main__":
    fetch_emails()
