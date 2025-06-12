from video_src.overview import overview_data

def get_video_overview(session_creds,videoid):
    response = overview_data(session_creds,videoid)
    return response