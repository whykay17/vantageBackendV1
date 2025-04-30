from datetime import datetime, timedelta
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from support import service_data, version_data

def get_best_video_data(session_creds, days):
    creds = Credentials(**session_creds)
    youtube = build(service_data, version_data, credentials=creds)

    video_list = get_all_videos(session_creds)
    range_videos = filter_videos_by_date(video_list, days)

    # Fetch video statistics
    video_stats = youtube.videos().list(
        part="statistics,snippet",
        id=",".join(range_videos)
    ).execute()

    return video_stats['items']

def get_all_videos(session_creds):
    creds = Credentials(**session_creds)
    youtube = build(service_data, version_data, credentials=creds)

    # Fetch the uploads playlist ID
    channel_response = youtube.channels().list(
        part="contentDetails",
        mine=True
    ).execute()

    uploads_playlist_id = channel_response['items'][0]['contentDetails']['relatedPlaylists']['uploads']

    # Fetch videos in the uploads playlist
    playlist_items = []
    next_page_token = None
    while True:
        playlist_response = youtube.playlistItems().list(
            part="snippet",
            playlistId=uploads_playlist_id,
            maxResults=50,
            pageToken=next_page_token
        ).execute()

        playlist_items.extend(playlist_response['items'])
        next_page_token = playlist_response.get('nextPageToken')
        if not next_page_token:
            break

    return playlist_items

def filter_videos_by_date(videos,range):
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=range)
    start_date_iso = start_date.isoformat("T") + "Z"
    end_date_iso = end_date.isoformat("T") + "Z"

    video_ids = []
    for item in videos:
        video_date = item['snippet']['publishedAt']
        if start_date_iso <= video_date <= end_date_iso:
            video_ids.append(item['snippet']['resourceId']['videoId'])

    if not video_ids:
        return {"message": "No videos found in the specified date range."}
    else:
        return video_ids