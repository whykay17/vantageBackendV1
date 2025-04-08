from datetime import datetime,timedelta
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

service_analytics = 'youtubeAnalytics'
service_data = 'youtube'
version_analytics = 'v2'
version_data = 'v3'

def get_overview(session_creds):
    creds = Credentials(**session_creds)
    youtube = build(service_data, version_data, credentials=creds)
    request = youtube.channels().list(part='snippet,statistics', mine=True)
    response = request.execute()
    channel = response["items"][0]
    
    return {
        'channelUrl': f'https://www.youtube.com/channel/{channel["id"]}',
        'channelName': channel['snippet']['title'],
        'profileUrl': channel['snippet']['thumbnails']['medium']['url'],
        'subscriberCount': channel['statistics']['subscriberCount']
    }

def get_period(dayGap,session_creds):
    creds = Credentials(**session_creds)
    youtube = build(service_analytics,version_analytics,credentials=creds)
    current_date = datetime.utcnow().date()
    start_date = current_date - timedelta(days=dayGap)
    past_date = start_date - timedelta(days=dayGap)
    currentStats=execute_api_request(
        client_library_function=youtube.reports().query,
        ids='channel==MINE',
        dimensions='day',
        metrics='views,comments,likes,estimatedMinutesWatched,subscribersGained,averageViewPercentage',
        sort='views',
        startDate=start_date.isoformat(),
        endDate=current_date.isoformat()
    )
    pastStats=execute_api_request(
        client_library_function=youtube.reports().query,
        ids='channel==MINE',
        dimensions='day',
        metrics='views,comments,likes,estimatedMinutesWatched,subscribersGained,averageViewPercentage',
        sort='views',
        startDate=past_date.isoformat(),
        endDate=start_date.isoformat()
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


def get_latest_video_id(session_creds):
    creds = Credentials(**session_creds)
    youtube = build(service_data, version_data, credentials=creds)
    request = youtube.search().list(
        part='snippet',
        forMine=True,
        type='video',
        order='date',
        maxResults=1
    )
    response = request.execute()
    return response["items"][0]["id"]["videoId"]

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

    # Convert publish_date to datetime object (assuming ISO 8601 format)
    publish_datetime = datetime.strptime(publish_date, "%Y-%m-%dT%H:%M:%SZ")
    start_date = publish_datetime.date().isoformat()
    end_date = (publish_datetime + timedelta(days=7)).date().isoformat()  # First 7 days stats

    response = execute_api_request(
        client_library_function=youtube_analytics.reports().query,
        ids='channel==MINE',
        metrics='views,estimatedMinutesWatched,averageViewDuration,averageViewPercentage,subscribersGained,shares',
        filters=f'video=={video_id}',
        startDate=start_date,
        endDate=end_date
    )

    # Format response for better readability
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

def formatAPIResponse(response):
    headers = [header['name'] for header in response['columnHeaders']]
    rows = response.get('rows',[])
    formatted_rows = []
    for row in rows:
        row_data = dict(zip(headers,row))
        formatted_rows.append(row_data)
    return formatted_rows

def execute_api_request(client_library_function, **kwargs):
  response = client_library_function(
    **kwargs
  ).execute()

  return response