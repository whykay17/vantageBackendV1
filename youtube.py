from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

def get_youtube_data(session_creds):
    creds = Credentials(**session_creds)
    youtube = build('youtube', 'v3', credentials=creds)
    request = youtube.channels().list(part='snippet,statistics', mine=True)
    response = request.execute()
    channel = response["items"][0]
    
    return {
        'channelUrl': f'https://www.youtube.com/channel/{channel["id"]}',
        'channelName': channel['snippet']['title'],
        'profileUrl': channel['snippet']['thumbnails']['medium']['url'],
        'subscriberCount': channel['statistics']['subscriberCount']
    }
