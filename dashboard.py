from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from support import version_data,service_data,execute_api_request
from dashboard_src.overview import get_overview_data
from dashboard_src.latest import get_latest_video_id,get_video_metadata,get_video_stats
from dashboard_src.period import get_period_history
from dashboard_src.best import get_best_video_data

def get_overview(session_creds):
    return get_overview_data(session_creds)

def get_period(dayGap,session_creds):
    return get_period_history(dayGap,session_creds)

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

def get_best_video(gap,session_creds):
    return get_best_video_data(session_creds,gap)