from datetime import datetime,timedelta
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from support import service_analytics, version_analytics

def get_gender_age(session_creds, dayGap):
    creds = Credentials(**session_creds)
    youtube_analytics = build(service_analytics, version_analytics, credentials=creds)

    end_date = datetime.utcnow().date()
    start_date = end_date - timedelta(days=dayGap)

    response = youtube_analytics.reports().query(
        ids='channel==MINE',
        startDate=start_date.strftime('%Y-%m-%d'),
        endDate=end_date.strftime('%Y-%m-%d'),
        metrics='viewerPercentage',
        dimensions='ageGroup,gender',
        sort='ageGroup'
    ).execute()

    rows = response.get("rows", [])

    age_gender_map = {}

    for row in rows:
        age_raw, gender, percentage = row
        age_group = age_raw.replace("age", "").replace("-", "+") if age_raw == "age65-" else age_raw.replace("age", "")
        
        if age_group not in age_gender_map:
            age_gender_map[age_group] = {"male": 0, "female": 0}
        
        age_gender_map[age_group][gender] = percentage

    age_order = ["13-17", "18-24", "25-34", "35-44", "45-54", "55-64", "65+"]
    labels = []
    male_data = []
    female_data = []

    for age in age_order:
        if age in age_gender_map:
            labels.append(age)
            male_data.append(age_gender_map[age].get("male", 0))
            female_data.append(age_gender_map[age].get("female", 0))

    chart_data = {
        "labels": labels,
        "datasets": [
            {
                "label": "Male",
                "data": male_data,
                "backgroundColor": "#3b82f6"
            },
            {
                "label": "Female",
                "data": female_data,
                "backgroundColor": "#ec4899"
            }
        ]
    }
    return chart_data

def get_country(session_creds, dayGap):
    creds = Credentials(**session_creds)
    youtube_analytics = build(service_analytics, version_analytics, credentials=creds)

    end_date = datetime.utcnow().date()
    start_date = end_date - timedelta(days=dayGap)

    response = youtube_analytics.reports().query(
        ids='channel==MINE',
        startDate=start_date.strftime('%Y-%m-%d'),
        endDate=end_date.strftime('%Y-%m-%d'),
        metrics='views',
        dimensions='country',
        sort='-views',
        maxResults=7
    ).execute()

    countryViews = [
        {
            'country': row[0],
            'Views': int(row[1])
        } for row in response.get('rows', [])
    ]
    return countryViews

def get_device(session_creds, dayGap):
    creds = Credentials(**session_creds)
    youtube_analytics = build(service_analytics, version_analytics, credentials=creds)

    end_date = datetime.utcnow().date()
    start_date = end_date - timedelta(days=dayGap)

    response = youtube_analytics.reports().query(
        ids='channel==MINE',
        startDate=start_date.strftime('%Y-%m-%d'),
        endDate=end_date.strftime('%Y-%m-%d'),
        metrics='views',
        dimensions='deviceType',
        sort='-views'
    ).execute()

    deviceData = {
        "labels": [],
        "datasets": [
            {
                "data": [],
                "backgroundColor": [
                    "#3b82f6",
                    "#10b981",
                    "#f59e0b",
                    "#8b5cf6",
                    "#ef4444",
                    "#6b7280"
                ],
                "borderWidth": 0
            }
        ],
    }

    for row in response.get('rows', []):
        device_type = row[0] if row[0] else "Unknown"
        views = int(row[1])
        deviceData['labels'].append(device_type)
        deviceData['datasets'][0]['data'].append(views)

    return deviceData
