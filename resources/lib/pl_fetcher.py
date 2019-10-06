import json, os, random, re, sys, time, urllib3,  xbmc, xbmcgui, xbmcvfs
import common as c


class get_Videos:
    def __init__(self):
        self.all_locations = sorted(c.aerial_data.keys()) #All available locations
        self.enabled_locations = c.get_enabled() #All user enabled locations
        self.local_locations = c.get_local() #All local locations

    #def creates a playlist streamable videos
    def stream_playlist(self):
        self.playlist = list()
        self.get_videolist()
        for item in self.videolist:
            print(item)
            self.process_video_data(item[0], item[1])
        return self.playlist

    #def creates a playlist of local videos
    def local_playlist(self):
        self.playlist = list()
        self.get_videolist()
        video_locations = list()
        for location in self.enabled_locations:
            for path in self.local_locations:
                path = os.path.join(c.download_folder, path)
                if location in path:
                    if not "My Videos" in location:
                        for quality in c.get_quality():
                            qual_path = c.validatePath(os.path.join(path, quality))
                            data = {qual_path:location}
                            video_locations.append(data)
                    else:
                        data = {path:location}
                        video_locations.append(data)
        for item  in video_locations:
            for path in item.keys():
                location = item[path]
                for video in c.listdir(path, files=True):
                    if not re.search(c.excludes, video):
                        video_path = c.validatePath(os.path.join(path, video))
                        id = os.path.splitext(video)[0]
                        for item in self.videolist:
                            if item[0] in location:
                                for video in item[1]:
                                    if id in video["id"]:
                                        self.process_video_data(item[0], [video], video_path)
        return self.playlist
    #def returns a videolist based on user settings
    def process_video_data(self, location, videos, url=None):
        # videolist = list()
        #def get apporiate url
        def get_url(url):
            if c.download_time == "Never":
                url = video.get("url-1080-H264")
                if url == "" or url == None:
                    url = video.get("url")
            # elif c.download_quality == "HD":
            #     url = video.get("url-1080-SDR")
            #     if url == "" or url == None:
            # elif c.download_quality == "4K":
            #     url = video.get("url-4K-SDR")
            #     if url == "" or url == None:
            #         url = None
            return url
        #def converts time to string
        def fix_time(t):
            if int(t) < 10:
                return "0{}".format(int(t))
            else:
                return int(t)
        #def cleans string
        def clean_string(text):
            return re.sub(r'[^\x00-\x7F]+',' ', text)
        #def converts sting to a time
        def convert_time(t):
            if int(t) < 60:
                min = 0
                sec = t
                end_min = 0
                end_sec = int(sec)+10
            else:
                dt = float(int(t)/60)
                min = int(dt)
                sec = (dt - min)*60
                end_min = min
                end_sec = int(sec)+10
            if int(end_sec) > 60:
                end_sec = int(end_sec)-60
                end_min+=1
            start = "00:{}:{},000".format(fix_time(min),fix_time(sec))
            end = "00:{}:{},000".format(fix_time(end_min),fix_time(end_sec))
            return ("{} --> {}".format(start, end))
        #def get apporiate video base on time setting
        def get_time(video):
            video_time = video.get("timeOfDay")
            c_time_of_day = c.time_of_day
            if "auto" in c_time_of_day:
                c_time_of_day = self.get_current_time()
            if c_time_of_day == video_time:
                return True
            elif "random" in c_time_of_day:
                # return bool(random.getrandbits(1))
                return True
            else:
                return False
        #def create a new dataset
        def convert_poi(poi=""):

            data = {
                    "url": url,
                    "id" : video_id,
               "location": location,
              "timeOfDay": video.get("timeOfDay"),
                    "poi": None
                    }
            if poi != "" and poi != None:
                poi_data = {}
                poi_len = len(poi)
                counter = 1
                for i in sorted(poi.keys()):
                    poi_data.update({# convert_time(i):
                                    i : clean_string(c.string_data[poi[i]])
                                    })
                data.update({"poi": poi_data})
            if "My Video" in location:
                data.update({"location": video_id})
            return data

        for video in videos:
            if get_time(video) == True:
                url = get_url(url)
                video_id = os.path.splitext(url.split('/')[-1])[0]
                video_id = os.path.splitext(url.split('\\')[-1])[0]
                self.playlist.append(convert_poi(video.get('pointsOfInterest')))
        return
    #def gets video data based on location
    def get_location_videos(self, location=""):
        videos = list()

        #def only gets videos from International Space Station
        def get_iss_videos(location):
            for video in c.aerial_data[location]["videos"]:
                if video["iss"] == "True":
                    videos.append(video)

        #def only gets videos not from ISS
        def get_videos(location):
            for video in c.aerial_data[location]["videos"]:
                if video["iss"] == "False":
                    videos.append(video)

        if location == "":
            for location in sorted(c.aerial_data.keys()):
                get_iss_videos(location)
        else:
            get_videos(location)
        return videos
    #def get current times
    def get_current_time(self):
        hr = time.localtime().tm_hour
        min = time.localtime().tm_min
        hr+=round(float(min)/60,1)
        dst = bool(time.localtime().tm_isdst)
        if dst:
            hr+=1
        if (hr > 5.5) and (hr < 17.5):
            return "day"
        else:
             return "night"
    #def gets local video data
    def get_local_videos(self, location):
        videos = list()
        path = os.path.join(c.download_folder, location)
        if os.path.isdir(path):
            for item in os.listdir(path):
                item_path = os.path.join(path, item)
                if not item_path.endswith(".info"):
                    if os.path.isfile(item_path):
                        data = {
                                "url": item_path,
                                "id" : os.path.splitext(item_path.split('/')[-1])[0],
                           "location": os.path.splitext(item_path.split('/')[-1])[0],
                          "timeOfDay": "",
                                "poi": ""
                                }
                        videos.append(data)
        return videos
    #def get list of videos for locations
    def get_videolist(self):
        self.videolist = list()
        for location in self.enabled_locations:
            if "Space Station" in location:
                videos = self.get_location_videos()
            elif location in self.all_locations:
                videos = self.get_location_videos(location)
            else:
                videos = self.get_local_videos(location)
            self.videolist.append((location, videos))


if __name__ == '__main__':
    get_Videos().stream_playlist()
