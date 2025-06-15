from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from support import service_analytics,version_analytics

def get_traffic_data(start_date, end_date, session_creds):
    creds = Credentials(**session_creds)
    youtube_analytics = build(service_analytics, version_analytics, credentials=creds)
    
    response = youtube_analytics.reports().query(
        ids='channel==MINE',
        startDate=start_date,
        endDate=end_date,
        metrics='views,estimatedMinutesWatched',
        dimensions='insightTrafficSourceType',
        sort='-views',
        maxResults=10
    ).execute()

    labels = []
    views = []
    watchTime = []

    for row in response.get('rows', []):
        labels.append(row[0])
        views.append(int(row[1]))
        watchTime.append(int(row[2]))

    return {
        'labels': labels,
        'views': views,
        'watchTime': watchTime
    }