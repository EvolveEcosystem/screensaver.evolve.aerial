import common as c, json, os, random, re, urllib3, sys, time, xbmcgui, xbmcvfs
cwd = os.path.dirname(__file__)
http = urllib3.PoolManager()
progress = xbmcgui.DialogProgress()

def beta(msg):
    c.beta("F.GVD.DOWNLOADER: {}".format(msg))


class Downloader:
    def __init__(self, *args, **kwargs):
        self.mode = kwargs['mode']
        self.aerial_data = c.aerial_data
        self.items = {}
    def download(self):
        def update(key):
            beta("Getting available Screensavers")
            progress.update(0, "%s" % key, "Getting available Screensavers")
            time.sleep(.5)
        def complete(key):
            beta("Download Complete")
            progress.update(100, "%s" % key, "Download Complete.")
            time.sleep(.5)
        if c.download_folder:
            if self.mode == 0 or self.mode == 1:
                beta("Getting available Screensavers")
                progress.create(c.heading, "Getting available Screensavers" )
            for location in c.get_enabled():
                directories = self.make_dir(location)
                videos = c.get_video_data(location)
                if not "My Videos" in location:
                    data = {location:{
                            "videos":videos,
                            "dir":directories}}
                    self.items.update(data)
            if self.mode == 0:
                for key in sorted(self.items.keys()):
                    item = self.items[key]
                    update(key)
                    self.process_video_data(key, item["videos"], item["dir"])
                    complete(key)
            if self.mode == 1 or self.mode == 2:
                key = random.choice(self.items.keys())
                item = self.items[key]
                if self.mode == 1:
                    update(key)
                self.process_video_data(key, item["videos"], item["dir"])
                if self.mode == 1:
                    complete(key)

            else:
                l1 = "You have download settings to Stream Only."
                l2 = "Change your settings if you would like to download videos"
                c.dialog.ok(c.heading, l1, l2)
            try:
                progress.close()
            except Exception as err:
                pass
            c.update_date(c.time())
        else:
            l1 = "Please set a download location."
            c.dialog.ok(c.heading, l1)
            sys.exit()
        return


    #def downloads videos to directorys made earlier
    def get_video(self, input, output, x, of_x, name):
        #def converts bytes to best size option
        def format_bytes(bytes_num):
            sizes = [ "B", "KB", "MB", "GB", "TB" ]
            i = 0
            dblbyte = bytes_num
            while (i < len(sizes) and  bytes_num >= 1024):
                dblbyte = bytes_num / 1024.0
                i = i + 1
                bytes_num = bytes_num / 1024
            return "%.02f %s" % (round(dblbyte, 2), sizes[i])
        chunk_size = 8192
        total_size = 0
        start_time = time.time()
        with http.request('GET',input, preload_content=False) as r:
            size = r.headers.get("Content-Length")
            str_size = format_bytes(int(size))
            if c.exists(output):
                if int(size) != int(c.file(output).size()):
                    os.remove(output)
                    # c.log("SIZE: {}".format(size))
                    # c.log(c.file(output).size())
                    # c.log("___________________JENNA")
            if not os.path.isfile(output):
                # with open(output, 'wb') as f:
                f =  c.file(output, 'w')
                for chunk in r.stream(chunk_size):
                    if chunk: # filter out keep-alive new chunks
                        f.write(chunk)
                        # f.flush()
                        total_size+=chunk_size
                        percent = min(int(total_size) * 100 / int(size), 100)
                        fetched_amount = format_bytes(int(total_size))
                        speed = int(int(total_size) / (time.time()-start_time))
                        eta = (int(size) - int(total_size)) / speed
                        if eta < 60:
                            eta = "{} secs".format(int(eta))
                        else:
                            m = round(eta/60)
                            sec = eta-(60*m)
                            eta = "{} mins {} secs".format(int(m), int(sec))
                        data = "{}[CR]Video {} of {}".format(name.title(), int(x), int(of_x))
                        data2 = "Downloading {} of {}".format(fetched_amount, str_size)
                        data3 = "Remaining Time: {}".format(eta)
                        data4 = "Downloading a screensaver from {}".format(name.title())
                        if self.mode == 0:
                            progress.update(percent,data, data2, data3)
                        if self.mode == 1:
                            progress.update(percent, data4, data2, data3)
                    if self.mode == 0 or self.mode == 1:
                        if progress.iscanceled():
                            f.close()
                            r.release_conn()
                            time.sleep(1)
                            os.remove(output)
                            sys.exit()
                f.close()
        r.release_conn()
        c.debug("Download Complete: %s" % output)

    #def get all video data and creates a info file with data
    def process_video_data(self, location, videos , directorys):
        self.vt = int(len(videos))*int(len(directorys))
        self.vc = 1
        # def gets accurate url
        def get_url(quality=""):
            if quality == 1080:
                url = video.get("url-1080-SDR")
                if url == "":
                    url = video["url"]
            else:
                url = video.get("url-4K-SDR")
                if url == "":
                    url = None
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
        def process_video(video):
            id = video['id']
            timeOfDay = video['timeOfDay']
            url_1080 = get_url(1080)
            url_4K = get_url()
            for directory in directorys:
                path = os.path.join(directory,"%s.mov" % id)
                if "4K" in directory:
                    if url_4K != None:
                        self.get_video(url_4K, path, self.vc, self.vt, location)
                else:
                    self.get_video(url_1080, path, self.vc, self.vt, location)
                self.vc+=1
        #interates throught videos
        if self.mode == 0:
            for video in videos:
                process_video(video)
        if self.mode ==1 or self.mode == 2:
            video = random.choice(videos)
            process_video(video)
        return



    #def makes directorys of location and quality options
    def make_dir(self, location):
        beta("Making Directories")
        quality_dir = list()
        loc_dir = os.path.join(c.download_folder, location)
        if not c.exists(loc_dir): c.mkdir(loc_dir)
        for qual in c.get_quality():
            beta("Download Quality: {}".format(qual))
            loc_qual_dir = os.path.join(loc_dir, qual)
            beta("Directory: {}".format(loc_qual_dir))
            if not "My Videos" in loc_qual_dir:
                if not c.exists(loc_qual_dir): c.mkdir(loc_qual_dir)
                quality_dir.append(loc_qual_dir)
        return quality_dir
