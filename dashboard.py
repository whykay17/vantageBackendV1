from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from support import version_data,service_data,execute_api_request
from dashboard_src.overview import get_overview_data
from dashboard_src.latest import get_latest_video_id,get_video_metadata,get_video_stats
from dashboard_src.period import get_period_history
from dashboard_src.best import get_all_videos,calculate_score,filter_videos_by_date

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

def get_best_video(days,session_creds):
    creds = Credentials(**session_creds)
    youtube = build(service_data, version_data, credentials=creds)

    video_list = get_all_videos(session_creds)
    range_videos = filter_videos_by_date(video_list, days)

    video_stats = youtube.videos().list(
        part="statistics,snippet",
        id=",".join(range_videos)
    ).execute()

    scored_videos = []
    for item in video_stats['items']:
        scored_videos.append(calculate_score(item))

    scores = [video["score"] for video in scored_videos]

    if not scores:
        return {"error":"No Videos Found"}
    else:
        best_score = max(scores)
        avg_score = sum(scores)/len(scores)
        if avg_score!=0:
            percent_score = (best_score-avg_score)/avg_score *100
        else:
            percent_score=0

    best_video = next (video for video in scored_videos if video['score'] == best_score )
    best_video["percentScore"]=percent_score
    return best_video