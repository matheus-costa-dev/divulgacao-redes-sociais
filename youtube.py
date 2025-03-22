from googleapiclient.discovery import build
from datetime import datetime
import isodate
from pandas import DataFrame, to_datetime
from typing import List
from yt_dlp import YoutubeDL

class Yt:
    def __init__(self,api_key:str, channel_id:str):
        self.service =  build("youtube","v3", developerKey=api_key)
        self.channel_id = channel_id

    def get_channel_info(self) -> dict:
        channel_res = self.service.channels().list(part="contentDetails", id=self.channel_id).execute()
        upload_playlist_id = channel_res["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]
        return upload_playlist_id

    def get_last_activity(self) -> dict:

        activity_response = self.service.activities().list(part="snippet",channelId=self.channel_id, maxResults=1).execute()
        last_activity = activity_response["items"][0].get("snippet").get("publishedAt")
        return last_activity
            
    def get_last_video(self) -> dict:
        upload_playlist_id = self.get_channel_info()
        playlist_res = self.service.playlistItems().list(part="snippet", playlistId=upload_playlist_id, maxResults=1, pageToken=None).execute()
        snippet = playlist_res["items"][0]["snippet"]
        data =  {
                "title": snippet["title"], 
                "description": snippet["description"], 
                "published_at":datetime.fromisoformat(snippet["publishedAt"]).replace(tzinfo=None).strftime("%Y-%m-%d %H:%M:%S"),
                "video_id":snippet["resourceId"]["videoId"],
                "url": f"https://www.youtube.com/watch?v={snippet["resourceId"]["videoId"]}"
                }
        
        return data

    def get_all_videos(self) -> List[dict]:
        upload_playlist_id = self.get_channel_info()
        page_next_token = None
        videos = []


        while True:
            playlist_res = self.service.playlistItems().list(part="snippet", playlistId=upload_playlist_id, maxResults=50, pageToken=page_next_token).execute()
            
            for item in playlist_res["items"]:
                snippet = item["snippet"]
                data =  {
                    "title": snippet["title"], 
                    "description": snippet["description"], 
                    #"published_at":datetime.fromisoformat(snippet["publishedAt"]).strftime("%Y-%m-%d %H:%M:%S"),
                    "published_at":datetime.fromisoformat(snippet["publishedAt"]),
                    "video_id":snippet["resourceId"]["videoId"],
                    "url_video": f"https://www.youtube.com/watch?v={snippet["resourceId"]["videoId"]}",
                    "url_shorts": f"https://www.youtube.com/shorts/{snippet["resourceId"]["videoId"]}"
                    }
                
                videos.append(data)

            page_next_token = playlist_res.get("nextPageToken")
            if page_next_token == None:
                break
        
        return videos
    
    def get_all_videos_info(self,video_ids:List[str]) -> List[dict]:

        if not video_ids:
            video_ids = [video["video_id"] for video in self.get_all_videos()]

        if len(video_ids) <= 50:
            assert len(video_ids) > 0 , "A lista de ids esta vazia, deve ter ao menos 1 id"

            if video_ids == 1:
                return self.get_videos_info(video_ids[0])
            
            videos_info = self.get_videos_info(video_ids)
            return videos_info
        else:
            n_times = (len(video_ids)/50).__ceil__()
            videos_info_list = []
            for i in range(n_times):
                part_video_ids = video_ids[50 * i : 50 * (i + 1)] 
                videos_info_list.append(self.get_videos_info(part_video_ids))

            
            flatten_videos_info = [item for nested in videos_info_list for item in nested]
               
            return flatten_videos_info


    def get_videos_info(self,video_ids:List[str]) -> List[dict]:
        video_response = self.service.videos().list(part="id,contentDetails", id=",".join(video_ids)).execute()
        videos_info = []
        for item  in video_response["items"]:
            data = {"video_id": item["id"], **item["contentDetails"]}
            data["duration"] = isodate.parse_duration(data["duration"]).total_seconds()
            data["is_shorts"] = True if data["duration"] <= 180 else False
            if data.get("regionRestriction"):
                data["regionRestriction"] = data["regionRestriction"]["blocked"] 
            videos_info.append(data)

        return videos_info


    def get_table(self, export:bool=False) -> DataFrame:
        df_videos = DataFrame(self.get_all_videos())
        videos_ids = df_videos["video_id"].to_list()
        df_videos_info = DataFrame(self.get_all_videos_info(video_ids=videos_ids))
        
        full_table = df_videos.merge(df_videos_info, "left", on="video_id")
        full_table["published_at"] = to_datetime(full_table['published_at'], utc=True).dt.tz_localize(None)
        if export:
            full_table.to_excel(f"tbls/{self.channel_id}.xlsx")
            return None

        return full_table
    

    def download_short(self,urls:List[str] ) -> None:

        assert isinstance(urls, list) , "as urls tem de ser uma lista"
        assert len(urls) > 0 , "a lista tem de ter pelo menos um item"

        ydl_opts = {"outtmpl": "videos/video.mp4"}
        with YoutubeDL(ydl_opts) as ydl:
            ydl.download(urls)

     
# api_key = "AIzaSyC3RBNJgDfDVEPgrGtAAg6spDVFPGHvPvU"
# channel_id = "UC52gcAONHi2DhPT2O1IwufQ"

# yt = youtube(api_key, channel_id)
# yt.get_last_video()

#https://www.youtube.com/watch?v=fA-2saKknTU