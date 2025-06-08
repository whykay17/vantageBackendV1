# auth.py
from flask import session, redirect, request
from google_auth_oauthlib.flow import Flow
import os
import pathlib
import json

os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"  # Disable HTTPS check in development

CLIENT_SECRETS_FILE = "client_secret.json"
SCOPES = ["https://www.googleapis.com/auth/youtube.readonly"]
REDIRECT_URI = "http://localhost:5000/oauth2callback"
TOKEN_FILE = "dev_token.json" #For development to keep authentication on during code change

def login():
    flow = Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE,
        scopes=SCOPES,
        redirect_uri=REDIRECT_URI
    )
    auth_url, state = flow.authorization_url(prompt='consent')
    session["state"] = state
    return redirect(auth_url)

def callback():
    state = session["state"]

    flow = Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE,
        scopes=SCOPES,
        state=state,
        redirect_uri=REDIRECT_URI
    )

    flow.fetch_token(authorization_response=request.url)
    credentials = flow.credentials

    with open(TOKEN_FILE, "w") as token_file:#stores credentials in local file
        json.dump({
            "token": credentials.token,
            "refresh_token": credentials.refresh_token,
            "token_uri": credentials.token_uri,
            "client_id": credentials.client_id,
            "client_secret": credentials.client_secret,
            "scopes": credentials.scopes
        }, token_file)

    # Store credentials in session
    session["credentials"] = {
        "token": credentials.token,
        "refresh_token": credentials.refresh_token,
        "token_uri": credentials.token_uri,
        "client_id": credentials.client_id,
        "client_secret": credentials.client_secret,
        "scopes": credentials.scopes
    }
    return redirect("http://localhost:4200/home")
