from flask import Flask, jsonify, session,request
from flask_cors import CORS
from auth import login, callback
from support import login_required
from dashboard import get_overview,get_latest_video,get_period,get_best_video,get_engagement,get_subscriber,get_traffic,get_retention,get_demographics
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

@app.route("/channel-overview")
@login_required
def overview_data():
    return jsonify(get_overview(session["credentials"]))

@app.route("/period-stats",methods=['GET'])
@login_required
def period_stats():
    dayGap= int(request.args.get('period', '7'))
    return jsonify(get_period(dayGap,session["credentials"]))

@app.route("/latest-video")
@login_required
def latest_stats():
    return jsonify(get_latest_video(session["credentials"]))

@app.route("/best-video",methods=['GET'])
@login_required
def best_video():
    dayGap= int(request.args.get('period', '7'))
    return jsonify(get_best_video(dayGap,session["credentials"]))

@app.route("/engagement",methods=['GET'])
@login_required
def engagement():
    dayGap= int(request.args.get('period', '7'))
    return jsonify(get_engagement(dayGap,session["credentials"]))

@app.route("/subscriber", methods=['GET'])
@login_required
def subscriber():
    dayGap= int(request.args.get('period', '7'))
    return jsonify(get_subscriber(dayGap, session["credentials"]))

@app.route("/traffic", methods=['GET'])
@login_required
def traffic():
    dayGap = int(request.args.get('period', '7'))
    return jsonify(get_traffic(dayGap, session["credentials"]))

@app.route("/retention", methods=['GET'])
@login_required
def retention():
    dayGap = int(request.args.get('period', '7'))
    return jsonify(get_retention(dayGap, session["credentials"]))

@app.route("/demographics", methods=['GET'])
@login_required
def demographics():
    dayGap = int(request.args.get('period', '7'))
    return jsonify(get_demographics(dayGap, session["credentials"]))

@app.route("/logout")
@login_required
def logout():
    session.clear()
    return jsonify({"message": "Logged out successfully."})

if __name__ == "__main__":
    app.run(host="localhost",port="5000",debug=True)
