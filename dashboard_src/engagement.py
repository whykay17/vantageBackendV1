from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from support import service_analytics,version_analytics
from datetime import datetime, timedelta
import math

def give_engagement(dayGap, session_creds):
    creds = Credentials(**session_creds)
    youtube_analytics = build(service_analytics, version_analytics, credentials=creds)

    end_date = datetime.utcnow().date()
    start_date = end_date - timedelta(days=dayGap)

    response = youtube_analytics.reports().query(
        ids='channel==MINE',
        startDate=start_date.strftime('%Y-%m-%d'),
        endDate=end_date.strftime('%Y-%m-%d'),
        metrics='likes,comments,shares',
        dimensions='day',
        sort='day'
    ).execute()

    return response.get('rows', [])  # just return rows directly

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
    
    bucket_count = min(10, len(engagement_data))
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

        line_data['labels'].append(label)
        line_data['likes'].append(total_likes)
        line_data['comments'].append(total_comments)
        line_data['shares'].append(total_shares)


    # if granularity == 'day':
    #     for day_data in engagement_data:
    #         line_data['labels'].append(day_data[0])
    #         line_data['likes'].append(day_data[1])
    #         line_data['comments'].append(day_data[2])
    #         line_data['shares'].append(day_data[3]) 
    # else:
    #     if granularity == 'week':
    #         divide=7
    #     elif granularity == 'month':
    #         divide=30
    #     base=0
    #     while base < len(engagement_data):
    #         for i in range(base, base+divide):
    #             total_likes = 0
    #             total_comments = 0
    #             total_shares = 0
    #             for i in range(divide):
    #                 total_likes += engagement_data[i]['likes']
    #                 total_comments += engagement_data[i]['comments']
    #                 total_shares += engagement_data[i]['shares']
    #             labelled_data = {
    #                 'date': day_data[base]['date'],
    #                 'likes': total_likes,
    #                 'comments': total_comments,
    #                 'shares': total_shares
    #             }
    #             line_data.append(labelled_data)  
    #         base += divide

    return line_data

    