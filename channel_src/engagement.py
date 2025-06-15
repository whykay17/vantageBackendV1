from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from support import service_analytics,version_analytics
from datetime import datetime, timedelta
import math

def give_engagement(start_date, end_date, session_creds):
    creds = Credentials(**session_creds)
    youtube_analytics = build(service_analytics, version_analytics, credentials=creds)

    response = youtube_analytics.reports().query(
        ids='channel==MINE',
        startDate=start_date,
        endDate=end_date,
        metrics='likes,comments,shares',
        dimensions='day',
        sort='day'
    ).execute()

    return response.get('rows', [])

def get_engagement_count(rows):
    engagement_count = {
        'likes': 0,
        'comments': 0,
        'shares': 0
    }

    for row in rows:
        engagement_count['likes'] += int(row[1])
        engagement_count['comments'] += int(row[2])
        engagement_count['shares'] += int(row[3])

    for key in engagement_count:
        if engagement_count[key] < 0:
            engagement_count[key] = 0

    return engagement_count


def get_line_data(engagement_data):
    labelCount = 10
    bucket_count = min(labelCount, len(engagement_data))
    line_data = {
        'labels': [],
        'likes': [],
        'comments': [],
        'shares': []
    }

    if not engagement_data:
        return line_data

    entry_count = len(engagement_data)
    bucket_size = math.ceil(entry_count / bucket_count)

    for i in range(0, entry_count, bucket_size):
        bucket = engagement_data[i:i + bucket_size]

        total_likes = sum(row[1] for row in bucket)
        total_comments = sum(row[2] for row in bucket)
        total_shares = sum(row[3] for row in bucket)

        label = bucket[-1][0]
        date_obj = datetime.strptime(label, "%Y-%m-%d")
        label_date = f"{date_obj.day}/{date_obj.month}/{date_obj.strftime('%y')}"

        line_data['labels'].append(label_date)
        line_data['likes'].append(total_likes)
        line_data['comments'].append(total_comments)
        line_data['shares'].append(total_shares)

    return line_data

    