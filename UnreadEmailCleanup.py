import base64
import mimetypes
import os
import os.path
from email.message import EmailMessage
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.text import MIMEText

import google.auth
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = ["https://mail.google.com/"]


def gmail_unread_emails():
    """read unread emails in gmail"""
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    # create gmail api client
    service = build("gmail", "v1", credentials=creds)

    results = (
        service.users()
        .messages()
        .list(userId="me", labelIds=["INBOX"], q="is:unread")
        .execute()
    )

    messages = results.get("messages", [])
    count = len(messages)
    totalcount = 0
    while count > 0:
        if not messages:
            print("No unread messages.")
        else:
            print(f"Found {len(messages)} messages")
            totalcount+=len(messages)
            for message in messages:
                msg = (
                    service.users()
                    .messages()
                    .modify(
                        userId="me",
                        id=message["id"],
                        body={"removeLabelIds": ["UNREAD"]},
                    )
                    .execute()
                )
                print(f' {msg["id"]} has been marked as read.')

        messages = results = (
            service.users()
            .messages()
            .list(userId="me", labelIds=["INBOX"], q="is:unread")
            .execute()
        ).get("messages", [])
        count = len(messages)

    if totalcount:
        print(f'Marked {totalcount} messages as unread.')
    print("No unread messages.")
    return


if __name__ == "__main__":
    gmail_unread_emails()
