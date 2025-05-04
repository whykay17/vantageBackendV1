from functools import wraps
from flask import session, jsonify
import json
import os

service_analytics = 'youtubeAnalytics'
service_data = 'youtube'
version_analytics = 'v2'
version_data = 'v3'

TOKEN_FILE = "dev_token.json"#for development

def execute_api_request(client_library_function, **kwargs):
  response = client_library_function(
    **kwargs
  ).execute()

  return response

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "credentials" not in session:
            if os.path.exists(TOKEN_FILE):
                with open(TOKEN_FILE, "r") as token_file:
                    session["credentials"] = json.load(token_file)
            else:
              return jsonify({"error": "Not authenticated"}), 401
        return f(*args, **kwargs)
    return decorated_function
