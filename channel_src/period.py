from datetime import datetime,timedelta
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from support import service_analytics,version_analytics,execute_api_request
from support import execute_api_request,formatAPIResponse

def get_period_history(start_date, end_date, session_creds):
    creds = Credentials(**session_creds)
    youtube = build(service_analytics, version_analytics, credentials=creds)

    past_date = datetime.strptime(start_date, '%Y-%m-%d') - timedelta(days=(datetime.strptime(end_date, '%Y-%m-%d') - datetime.strptime(start_date, '%Y-%m-%d')).days)

    currentStats = execute_api_request(
        client_library_function=youtube.reports().query,
        ids='channel==MINE',
        dimensions='day',
        metrics='views,comments,likes,estimatedMinutesWatched,subscribersGained,averageViewPercentage',
        sort='views',
        startDate=start_date,
        endDate=end_date
    )
    pastStats = execute_api_request(
        client_library_function=youtube.reports().query,
        ids='channel==MINE',
        dimensions='day',
        metrics='views,comments,likes,estimatedMinutesWatched,subscribersGained,averageViewPercentage',
        sort='views',
        startDate=past_date.strftime('%Y-%m-%d'),
        endDate=start_date
    )

    formatDataCurrent = formatAPIResponse(currentStats)
    formatDataPast = formatAPIResponse(pastStats)

    current_summary = summarize_period_data(formatDataCurrent)
    past_summary = summarize_period_data(formatDataPast)

    return {
        "current": current_summary,
        "previous": past_summary
    }


def summarize_period_data(data):
    summary = {
        "views": 0,
        "comments": 0,
        "likes": 0,
        "estimatedMinutesWatched": 0,
        "subscribersGained": 0,
        "averageViewPercentage": 0.0
    }
    count=0
    for day in data:
        summary["views"] += day.get("views", 0)
        summary["comments"] += day.get("comments", 0)
        summary["likes"] += day.get("likes", 0)
        summary["estimatedMinutesWatched"] += day.get("estimatedMinutesWatched", 0)
        summary["subscribersGained"] += day.get("subscribersGained", 0)
        summary["averageViewPercentage"] += day.get("averageViewPercentage", 0.0)
        count+=1
    if(count!=0):
        summary['averageViewPercentage']/=count
    return summary   