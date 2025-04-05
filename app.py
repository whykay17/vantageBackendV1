from flask import Flask, jsonify, session
from flask_cors import CORS
from auth import login, callback
from support import login_required
from youtube import get_youtube_data
import os

app = Flask(__name__)
CORS(app, supports_credentials=True)

app.secret_key = os.urandom(24)  # Replace with env variable in production

@app.route("/login")
def login_route():
    return login()

@app.route("/oauth2callback")
def callback_route():
    return callback()

@app.route('/check-auth')
@login_required
def check_auth():
    return jsonify(authenticated='credentials' in session)

@app.route("/youtube-data")
@login_required
def youtube_data():
    return jsonify(get_youtube_data(session["credentials"]))

@app.route("/logout")
@login_required
def logout():
    session.clear()
    return jsonify({"message": "Logged out successfully."})

if __name__ == "__main__":
    app.run(host="localhost",port="5000",debug=True)
