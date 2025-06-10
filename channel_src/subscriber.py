from datetime import datetime, timedelta
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from support import service_analytics, version_analytics
import math

def get_subscriber_change(dayGap, session):
    creds = Credentials(**session)
    youtube_analytics = build(service_analytics, version_analytics, credentials=creds)

    end_date = datetime.utcnow().date()
    start_date = end_date - timedelta(days=dayGap)

    response = youtube_analytics.reports().query(
        ids='channel==MINE',
        startDate=start_date.strftime('%Y-%m-%d'),
        endDate=end_date.strftime('%Y-%m-%d'),
        metrics='subscribersGained,subscribersLost',
        dimensions='day',
        sort='day'
    ).execute()

    return get_stack_data(response.get('rows', []))

def get_stack_data(data):
    stack_data = {
        'labels': [],
        'subscribersGained': [],
        'subscribersLost': []
    }

    bucket_count = 15
    entry_count = len(data)
    bucket_size = math.ceil(entry_count / bucket_count)

    for i in range(0, entry_count, bucket_size):
        bucket = data[i:i + bucket_size]

        total_gained = sum(int(row[1]) for row in bucket)
        total_lost = sum(int(row[2]) for row in bucket)

        label = bucket[-1][0]
        date_obj = datetime.strptime(label, "%Y-%m-%d")
        label_date = f"{date_obj.day}/{date_obj.month}/{date_obj.strftime('%y')}"

        stack_data['labels'].append(label_date)
        stack_data['subscribersGained'].append(total_gained)
        stack_data['subscribersLost'].append('-'+str(total_lost))

    return stack_data