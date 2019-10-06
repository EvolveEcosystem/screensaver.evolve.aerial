import common, json, os, re, urllib3, sys, time, xbmcgui

#set global variables
cwd = os.path.dirname(__file__)
aerial_data = common.aerial_data
string_data = common.string_data
http = urllib3.PoolManager()
progress = xbmcgui.DialogProgress()
mode = 0
get_one = False

#def makes directorys of location and quality options
def make_dir(location):
    print(location)
    quality_dir = list()
    loc_dir = os.path.join(common.download_folder, location)
    if not os.path.isdir(loc_dir):
        os.mkdir(loc_dir)
    for qual in common.get_quality():
        loc_qual_dir = os.path.join(loc_dir, qual)
        if not os.path.isdir(loc_qual_dir):
            os.mkdir(loc_qual_dir)
        quality_dir.append(loc_qual_dir)
    return quality_dir

#def takes video location and produces a list of video objects
def get_video_data(location=""):
    videos = list()

    #def only gets videos from International Space Station
    def get_iss_videos(location):
        for video in aerial_data[location]["videos"]:
            if video["iss"] == "True":
                videos.append(video)

    #def only gets videos not from ISS
    def get_videos(location):
        for video in aerial_data[location]["videos"]:
            if video["iss"] == "False":
                videos.append(video)

    if location == "":
        for location in sorted(aerial_data.keys()):
            get_iss_videos(location)
    else:
        get_videos(location)
    return videos

#def downloads videos to directorys made earlier
def downloader(input, output, x, of_x, name):

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
        if os.path.isfile(output):
            if int(size) != int(os.path.getsize(output)):
                os.remove(output)
        if not os.path.isfile(output):
            if get_one != True:
                with open(output, 'wb') as f:
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
                            if mode == 0:
                                progress.update(percent,data, data2, data3)
                        if mode == 0:
                            if progress.iscanceled():
                                sys.exit()


                f.close()
                if mode == 1:
                    get_one = True
    r.release_conn()
    common.debug("Download Complete: %s" % output)

#def get all video data and creates a info file with data
def process_video_data(location, videos , directorys):

    #def gets accurate url
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
    #def writes pertinent infromation to file
    def create_poi(poi, directory):
        poi_file = os.path.join(directory, video_id+".info")
        if not os.path.isfile(poi_file):
            with open(poi_file, "w") as f:
                f.write("location[%s]\n" % location)
                f.write("time[%s]\n" % timeOfDay)
                if poi != "":
                    poi_len = len(poi)
                    counter = 1
                    for i in sorted(poi.keys()):
                        f.write("\n%s\n" % counter)
                        f.write("%s\n" % convert_time(i))
                        f.write("%s\n" % clean_string(string_data[poi[i]]))
                        counter +=1
            f.close()
    #interates throught videos
    v_t = len(videos)
    v_c = 1
    for video in videos:
        id = video['id']
        timeOfDay = video['timeOfDay']
        url_1080 = get_url(1080)
        url_4K = get_url()
        video_id = os.path.splitext(url_1080.split('/')[-1])[0]
        if get_one != True:
            for directory in directorys:
                if "4K" in directory:
                    if url_4K != None:
                        downloader(
                            url_4K,
                            os.path.join(directory, url_1080.split('/')[-1]),
                            v_c,
                            v_t,
                            location
                                )
                        # create_poi(video['pointsOfInterest'], directory)

                else:
                    downloader(
                        url_1080,
                        os.path.join(directory, url_1080.split('/')[-1]),
                        v_c,
                        v_t,
                        location
                            )
                    # create_poi(video['pointsOfInterest'], directory)
        v_c+=1

#def get all location data
def main():
    if mode == 0:
        progress.create(common.heading)
    #interates throught locations
    for location in common.get_enabled():
        if mode == 0:
            progress.update(0, "Getting Videos for %s" % location)
            time.sleep(.5)
        print(location)
        directorys = make_dir(location)

        # if "Space Station" in location:
        #     videos = get_video_data()
        # elif not "Custom" in location:
        #     videos = get_video_data(location)
        # if not "Custom" in location:
        #     process_video_data(location, videos, directorys)
        #     if mode == 0:
        #         progress.update(0, "All videos for %s have been downloaded." % location)
        #         time.sleep(1.5)

# if __name__ == '__main__':
#     if len(sys.argv) > 1:
#         if "silent" in sys.argv[1]:
#             global mode
#             mode = 1
#     main()
