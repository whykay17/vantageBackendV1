from support import service_data,version_data,service_analytics,version_analytics,formatAPIResponse,parse_duration
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from datetime import datetime,timedelta

def overview_data(session_creds,videoid):
    creds = Credentials(**session_creds)
    youtube = build(service_data, version_data, credentials=creds)
    analytics = build(service_analytics,version_analytics,credentials=creds)

    end_date = datetime.utcnow().date()
    start_date = end_date - timedelta(days=2800)

    data_response = youtube.videos().list(
        part="snippet,contentDetails,status",
        id=videoid
    ).execute()
    if not data_response["items"]:
        return {"error": "Video not found"}

    video = data_response["items"][0]
    snippet = video["snippet"]
    content_details = video["contentDetails"]
    status = video["status"]
    thumbnail_url = snippet["thumbnails"]["medium"]["url"]

    analytics_response = analytics.reports().query(
        ids="channel==MINE",
        startDate=start_date.isoformat(),
        endDate=end_date.isoformat(),
        metrics="views,likes,comments,shares,subscribersGained,subscribersLost,estimatedMinutesWatched,averageViewDuration,averageViewPercentage",
        filters=f"video=={videoid}",
        dimensions="video",
    ).execute()
    if not analytics_response:
        return {"error":"Analytics not found"}

    formatted_analytics=formatAPIResponse(analytics_response)

    return {
        "videoId": videoid,
        "videoUrl":f'https://www.youtube.com/watch?v={videoid}',
        "title": snippet["title"],
        "publishedAt": snippet["publishedAt"],
        "tags": snippet["tags"][0:4],
        "category":getCategory(snippet["categoryId"]),
        "duration": parse_duration(content_details["duration"]),
        "privacyStatus": status["privacyStatus"],
        "thumbnailUrl": thumbnail_url,
        "stats":formatStats(formatted_analytics[0])
    }

def formatStats(stats):
    return [
        { "label": "Views", "value": stats["views"]},
        { "label": "Likes", "value": stats["likes"]},
        { "label": "Comments", "value": stats["comments"] },
        { "label": "Shares", "value": stats["shares"] },
        { "label": "Watch Time", "value": stats["estimatedMinutesWatched"] },
        {
            "label": "Avg Duration",
            "value": stats["averageViewDuration"]
        },
        {
            "label": "Avg View %",
            "value": f"{stats['averageViewPercentage']}%"
        },
        { "label": "Subs Gained", "value": stats["subscribersGained"]},
        { "label": "Subs Lost", "value": stats["subscribersLost"] },
    ]

def getCategory(categoryid):
    categories = {
        "1": "Film & Animation",
        "2": "Autos & Vehicles",
        "10": "Music",
        "15": "Pets & Animals",
        "17": "Sports",
        "18": "Short Movies",
        "19": "Travel & Events",
        "20": "Gaming",
        "21": "Videoblogging",
        "22": "People & Blogs",
        "23": "Comedy",
        "24": "Entertainment",
        "25": "News & Politics",
        "26": "Howto & Style",
        "27": "Education",
        "28": "Science & Technology",
        "29": "Nonprofits & Activism",
        "30": "Movies",
        "31": "Anime/Animation",
        "32": "Action/Adventure",
        "33": "Classics",
        "34": "Comedy",
        "35": "Documentary",
        "36": "Drama",
        "37": "Family",
        "38": "Foreign",
        "39": "Horror",
        "40": "Sci-Fi/Fantasy",
        "41": "Thriller",
        "42": "Shorts",
        "43": "Shows",
        "44": "Trailers"
    }
    return categories.get(categoryid, "Unknown")

