from functools import wraps
from flask import session, jsonify
import json
import os
import isodate

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

def formatAPIResponse(response):
    headers = [header['name'] for header in response['columnHeaders']]
    rows = response.get('rows',[])
    formatted_rows = []
    for row in rows:
        row_data = dict(zip(headers,row))
        formatted_rows.append(row_data)
    return formatted_rows

def parse_duration(duration_str):
  duration = isodate.parse_duration(duration_str)
  total_seconds = int(duration.total_seconds())
  minutes, seconds = divmod(total_seconds, 60)
  hours, minutes = divmod(minutes, 60)

  if hours:
      return f"{hours}h {minutes}m {seconds}s"
  else:
      return f"{minutes}m {seconds}s"