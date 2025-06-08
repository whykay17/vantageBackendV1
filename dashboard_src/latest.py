from datetime import datetime,timedelta
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from support import service_data,version_data,service_analytics,version_analytics
from support import execute_api_request

def get_latest_video_id(session_creds):
    creds = Credentials(**session_creds)
    youtube = build(service_data, version_data, credentials=creds)

    channel_response = youtube.channels().list(
        part="contentDetails",
        mine=True
    ).execute()

    uploads_playlist_id = channel_response['items'][0]['contentDetails']['relatedPlaylists']['uploads']

    playlist_response = youtube.playlistItems().list(
        part="snippet",
        playlistId=uploads_playlist_id,
        maxResults=1
    ).execute()

    return playlist_response['items'][0]['snippet']['resourceId']['videoId']

def get_video_metadata(video_id, session_creds):
    creds = Credentials(**session_creds)
    youtube = build(service_data, version_data, credentials=creds)

    request=youtube.videos().list(
        part="snippet,statistics",
        id=video_id
    )
    response = request.execute()

    video=response["items"][0]
    stats=video["statistics"]
    snippet=video["snippet"]

    return {
        'title': snippet['title'],
        'publishedAt': snippet['publishedAt'],
        'thumbnail': snippet['thumbnails']['medium']['url'],
        'views': int(stats.get('viewCount', 0)),
        'likes': int(stats.get('likeCount', 0)),
        'comments': int(stats.get('commentCount', 0))
    }

def get_video_stats(video_id, publish_date, session_creds):
    creds = Credentials(**session_creds)
    youtube_analytics = build(service_analytics, version_analytics, credentials=creds)

    publish_datetime = datetime.strptime(publish_date, "%Y-%m-%dT%H:%M:%SZ")
    start_date = publish_datetime.date().isoformat()
    end_date = (publish_datetime + timedelta(days=7)).date().isoformat()

    response = execute_api_request(
        client_library_function=youtube_analytics.reports().query,
        ids='channel==MINE',
        metrics='views,estimatedMinutesWatched,averageViewDuration,averageViewPercentage,subscribersGained,shares',
        filters=f'video=={video_id}',
        startDate=start_date,
        endDate=end_date
    )

    headers = [header['name'] for header in response.get('columnHeaders', [])]
    rows = response.get('rows', [])

    if rows:
        values = rows[0]
        return dict(zip(headers, values))
    else:
        return {
            "views": 0,
            "estimatedMinutesWatched": 0,
            "averageViewDuration": 0,
            "averageViewPercentage": 0.0,
            "subscribersGained": 0,
            "shares": 0
        }