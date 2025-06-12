from math import ceil
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from support import service_data, version_data

def get_video_list(session_creds):
    creds = Credentials(**session_creds)
    youtube = build(service_data, version_data, credentials=creds)

    channel_response = youtube.channels().list(
        part="contentDetails",
        mine=True
    ).execute()

    uploads_playlist_id = channel_response['items'][0]['contentDetails']['relatedPlaylists']['uploads']

    videos = []
    next_page_token = None

    while True:
        playlist_response = youtube.playlistItems().list(
            part="snippet",
            playlistId=uploads_playlist_id,
            maxResults=50,
            pageToken=next_page_token
        ).execute()

        for item in playlist_response['items']:
            snippet = item['snippet']
            video_id = snippet['resourceId']['videoId']

            videos.append({
                "id": video_id,
                "title": snippet['title'],
                "thumbnailUrl": f"https://i.ytimg.com/vi/{video_id}/mqdefault.jpg",
                # "thumbnailUrl": snippet['thumbnails']['medium']['url'],
                "publishedOn": snippet['publishedAt'],
            })

        next_page_token = playlist_response.get('nextPageToken')
        if not next_page_token:
            break
    return videos