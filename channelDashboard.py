from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from support import version_data,service_data
from channel_src.overview import get_overview_data
from channel_src.latest import get_latest_video_id,get_video_metadata,get_video_stats
from channel_src.period import get_period_history
from channel_src.best import get_all_videos,calculate_score,filter_videos_by_date
from channel_src.engagement import give_engagement,get_engagement_count,get_line_data
from channel_src.subscriber import get_subscriber_change
from channel_src.traffic import get_traffic_data
from channel_src.retention import get_retention_data, get_sum_retention, get_retention_score
from channel_src.demographics import get_gender_age,get_country, get_device

def get_overview(session_creds):
    return get_overview_data(session_creds)

def get_period(start_date, end_date, session_creds):
    return get_period_history(start_date, end_date, session_creds)

def get_latest_video(session_creds):
    video_id = get_latest_video_id(session_creds)
    metadata=get_video_metadata(video_id,session_creds)
    stats=get_video_stats(video_id,metadata["publishedAt"],session_creds)
    return {
        'videoId': video_id,
        'url': f'https://www.youtube.com/watch?v={video_id}',
        **metadata,
        **stats
    }

def get_best_video(start_date, end_date, session_creds):
    creds = Credentials(**session_creds)
    youtube = build(service_data, version_data, credentials=creds)

    video_list = get_all_videos(session_creds)
    range_videos = filter_videos_by_date(video_list, start_date, end_date)

    video_stats = youtube.videos().list(
        part="statistics,snippet",
        id=",".join(range_videos)
    ).execute()

    scored_videos = []
    for item in video_stats['items']:
        scored_videos.append(calculate_score(item))

    scores = [video["score"] for video in scored_videos]

    if not scores:
        return {"error": "No Videos Found"}
    else:
        best_score = max(scores)
        avg_score = sum(scores) / len(scores)
        if avg_score != 0:
            percent_score = (best_score - avg_score) / avg_score * 100
        else:
            percent_score = 0

    best_video = next(video for video in scored_videos if video['score'] == best_score)
    best_video["percentScore"] = percent_score
    return best_video

def get_engagement(start_date, end_date, session_creds):
    engagement_by_day = give_engagement(start_date, end_date, session_creds)
    pieData = get_engagement_count(engagement_by_day)
    lineData = get_line_data(engagement_by_day)
    response = {
        'likes': pieData['likes'],
        'comments': pieData['comments'],
        'shares': pieData['shares'],
        'line_data': lineData
    }
    return response

def get_subscriber(start_date, end_date, session_creds):
    return get_subscriber_change(start_date, end_date, session_creds)

def get_traffic(start_date, end_date, session_creds):
    return get_traffic_data(start_date, end_date, session_creds)

def get_retention(start_date, end_date, session_creds):
    retentionData = get_retention_data(start_date, end_date, session_creds)
    tileData = get_sum_retention(retentionData)
    lineData = get_retention_score(retentionData)
    response = {
        'views': tileData['totalViews'],
        'engagedViews': tileData['totalEngagedViews'],
        'averageViewPercentage': tileData['averageViewPercentage'],
        'averageViewDuration': tileData['averageViewDuration'],
        'line_data': lineData
    }
    return response

def get_demographics(start_date, end_date, session_creds):
    gender_age_data = get_gender_age(session_creds, start_date, end_date)
    country_data = get_country(session_creds, start_date, end_date)
    device_data = get_device(session_creds, start_date, end_date)
    return {
        'gender_age': gender_age_data,
        'country': country_data,
        'device': device_data
    }