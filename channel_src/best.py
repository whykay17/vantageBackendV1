from datetime import datetime, timedelta
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from support import service_data, version_data
import math

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

def filter_videos_by_date(videos, start_date, end_date):
    start_date_iso = datetime.strptime(start_date, "%Y-%m-%d").isoformat("T") + "Z"
    end_date_iso = datetime.strptime(end_date, "%Y-%m-%d").isoformat("T") + "Z"

    video_ids = []
    for item in videos:
        video_date = item['snippet']['publishedAt']
        if start_date_iso <= video_date <= end_date_iso:
            video_ids.append(item['snippet']['resourceId']['videoId'])

    if not video_ids:
        return {"message": "No videos found in the specified date range."}
    else:
        return video_ids
    
def calculate_score(video):
    likes=int(video['statistics']['likeCount'])
    dislikes=int(video['statistics']['dislikeCount'])
    views=int(video['statistics']['viewCount'])
    comments=int(video['statistics']['commentCount'])
    engagementScore=(likes+dislikes+comments)/(views+1)
    sentimentScore=likes/(likes+dislikes+1)
    commentsScore=1+math.log((comments+1),10)
    score=engagementScore*sentimentScore*commentsScore
    return {
            "id":video['id'],
            "url":f'https://www.youtube.com/watch?v={video["id"]}',
            'publishedAt': video['snippet']['publishedAt'],
            "title":video['snippet']["title"],
            "thumbnail":video['snippet']["thumbnails"]["medium"]["url"],
            "score":score,
    }