from flask import Flask, jsonify, session,request
from flask_cors import CORS
from auth import login, callback
from support import login_required
from channelDashboard import get_overview,get_latest_video,get_period,get_best_video,get_engagement,get_subscriber,get_traffic,get_retention,get_demographics
from videos import get_video_list
from videoDashboard import get_video_overview
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

@app.route("/channel/overview")
@login_required
def overview_data():
    return jsonify(get_overview(session["credentials"]))

@app.route("/channel/period-stats", methods=['GET'])
@login_required
def period_stats():
    start_date = request.args.get('start', None)
    end_date = request.args.get('end', None)
    if not start_date or not end_date:
        return jsonify({"error": "Start and end dates are required"}), 400
    return jsonify(get_period(start_date, end_date, session["credentials"]))


@app.route("/channel/latest-video")
@login_required
def latest_stats():
    return jsonify(get_latest_video(session["credentials"]))

@app.route("/channel/best-video", methods=['GET'])
@login_required
def best_video():
    start_date = request.args.get('start', None)
    end_date = request.args.get('end', None)
    if not start_date or not end_date:
        return jsonify({"error": "Start and end dates are required"}), 400
    return jsonify(get_best_video(start_date, end_date, session["credentials"]))

@app.route("/channel/engagement", methods=['GET'])
@login_required
def engagement():
    start_date = request.args.get('start', None)
    end_date = request.args.get('end', None)
    if not start_date or not end_date:
        return jsonify({"error": "Start and end dates are required"}), 400
    return jsonify(get_engagement(start_date, end_date, session["credentials"]))

@app.route("/channel/subscriber", methods=['GET'])
@login_required
def subscriber():
    start_date = request.args.get('start', None)
    end_date = request.args.get('end', None)
    if not start_date or not end_date:
        return jsonify({"error": "Start and end dates are required"}), 400
    return jsonify(get_subscriber(start_date, end_date, session["credentials"]))

@app.route("/channel/traffic", methods=['GET'])
@login_required
def traffic():
    start_date = request.args.get('start', None)
    end_date = request.args.get('end', None)
    if not start_date or not end_date:
        return jsonify({"error": "Start and end dates are required"}), 400
    return jsonify(get_traffic(start_date, end_date, session["credentials"]))

@app.route("/channel/retention", methods=['GET'])
@login_required
def retention():
    start_date = request.args.get('start', None)
    end_date = request.args.get('end', None)
    if not start_date or not end_date:
        return jsonify({"error": "Start and end dates are required"}), 400
    return jsonify(get_retention(start_date, end_date, session["credentials"]))

@app.route("/channel/demographics", methods=['GET'])
@login_required
def demographics():
    start_date = request.args.get('start', None)
    end_date = request.args.get('end', None)
    if not start_date or not end_date:
        return jsonify({"error": "Start and end dates are required"}), 400
    return jsonify(get_demographics(start_date, end_date, session["credentials"]))

@app.route("/video/list")
@login_required
def video_list():
    return jsonify(get_video_list(session["credentials"]))

@app.route("/video/overview",methods=['GET'])
@login_required
def video_overview():
    videoid = request.args.get('vid','False')
    return jsonify(get_video_overview(session["credentials"],videoid))

@app.route("/logout")
@login_required
def logout():
    session.clear()
    return jsonify({"message": "Logged out successfully."})

if __name__ == "__main__":
    app.run(host="localhost",port="5000",debug=True)
