from datetime import datetime,timedelta
import math
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from support import service_analytics, version_analytics

def get_retention_data(start_date, end_date, session_creds):
    creds = Credentials(**session_creds)
    youtube_analytics = build(service_analytics, version_analytics, credentials=creds)

    response = youtube_analytics.reports().query(
        ids='channel==MINE',
        startDate=start_date,
        endDate=end_date,
        metrics="views,engagedViews,averageViewPercentage,averageViewDuration",
        dimensions='day',
        sort='day'
    ).execute()

    return response.get('rows', [])


def get_sum_retention(data):
    total_views = 0
    total_engaged_views = 0
    total_percentage = 0
    total_duration = 0

    for row in data:
        total_views += int(row[1])
        total_engaged_views += int(row[2])
        total_percentage += float(row[3])
        total_duration += float(row[4])

    if len(data) > 0:
        average_percentage = total_percentage / len(data)
        average_duration = total_duration / len(data)
    else:
        average_percentage = 0
        average_duration = 0

    return {
        'totalViews': total_views,
        'totalEngagedViews': total_engaged_views,
        'averageViewPercentage': average_percentage,
        'averageViewDuration': average_duration
    }

def get_retention_score(retention_data):
    labelCount = 10
    bucket_count = min(labelCount, len(retention_data))

    lineData = {
        'labels': [],
        'views': [],
        'engagedViews': [],
        'retentionPercentage': []
    }

    entry_count = len(retention_data)
    bucket_size = math.ceil(entry_count / bucket_count)

    for i in range(0, entry_count, bucket_size):
        row = retention_data[i]
        date = row[0]
        views = int(row[1])
        engaged_views = int(row[2])
        retention_percentage = engaged_views / views * 100 if views > 0 else 0

        lineData['labels'].append(date)
        lineData['views'].append(views)
        lineData['engagedViews'].append(engaged_views)
        lineData['retentionPercentage'].append(retention_percentage)

    return lineData