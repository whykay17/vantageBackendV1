from functools import wraps
from flask import session, jsonify

service_analytics = 'youtubeAnalytics'
service_data = 'youtube'
version_analytics = 'v2'
version_data = 'v3'

def execute_api_request(client_library_function, **kwargs):
  response = client_library_function(
    **kwargs
  ).execute()

  return response

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "credentials" not in session:
            return jsonify({"error": "Not authenticated"}), 401
        return f(*args, **kwargs)
    return decorated_function
