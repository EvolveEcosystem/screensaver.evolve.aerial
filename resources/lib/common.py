import datetime, json, os, xbmc, xbmcaddon, xbmcgui, xbmcvfs

#set true global variables
addon = xbmcaddon.Addon()
path = addon.getAddonInfo("path").decode("utf-8")
version = addon.getAddonInfo('version')
cwd = os.path.dirname(__file__)
dialog = xbmcgui.Dialog()
time_of_day = addon.getSetting("time_of_day").lower()
mode = addon.getSetting("mode")
audio = addon.getSetting("audio")
video = addon.getSetting("video")
playback_quality = addon.getSetting("playback_quality")
download_time = addon.getSetting("download_time")
download_quality = addon.getSetting("download_quality")
china_select = addon.getSetting("china_select")
dubai_select = addon.getSetting("dubai_select")
greenland_select = addon.getSetting("greenland_select")
hawaii_select = addon.getSetting("hawaii_select")
hong_kong_select = addon.getSetting("hong_kong_select")
iss_select = addon.getSetting("iss_select")
liwa_select = addon.getSetting("liwa_select")
london_select = addon.getSetting("london_select")
la_select = addon.getSetting("la_select")
ny_select = addon.getSetting("ny_select")
san_fran_select = addon.getSetting("san_fran_select")
sea_select = addon.getSetting("sea_select")
custom_select = addon.getSetting("custom_select")
heading="Evolve: Apple TV Screensavers"
name = addon.getAddonInfo("name")
update = os.path.join(addon.getAddonInfo("profile"), "update.json")
last_updated = xbmc.translatePath(update)
aerial_data = json.load(open(os.path.join(cwd,"aerial.json")))
string_data = json.load(open(os.path.join(cwd, "aerial_strings.json")))
excludes = ".(jpg|png|idx|srt|sfnfo|nfo|sub|db|txt|gif|xml)"

def audio_mode():
    if audio == "Stop audio":
        return 1
    elif audio == "Keep playing audio":
        return 2
    else:
        return 3
def video_mode():
    if video == "Keep playing video":
        return 1
    else:
        return 2
#def logs to kodi log
def log(msg):
    xbmc.log("{}".format(msg))
#def creates a notifcation in kodi
def notifcation(msg, heading="Evolve: Aerial Screensavers", time=5000):
    dialog.notification(heading, "{}".format(msg), icon="", time=time)
#def creates a ok dialog in kodi
def ok(msg, heading="Evolve: Aerial Screensavers"):
    dialog.ok(heading,"{}".format(msg))
#def sends info to kodi debug log
def debug(msg):
    xbmc.log(msg, xbmc.LOGDEBUG)
def beta(msg):
    if int(version.split(".")[1]) < 1:
        debug("EVOLVE_BETA_DEBUG: {}".format(msg))
#def creates a list of user selected location to use.
def get_enabled():
    locations = list()
    if custom_select == "true":
        locations.append("My Videos")
    if china_select == "true":
        locations.append("China")
    if dubai_select == "true":
        locations.append("Dubai")
    if greenland_select == "true":
        locations.append("Greenland")
    if hawaii_select == "true":
        locations.append("Hawaii")
    if hong_kong_select == "true":
        locations.append("Hong Kong")
    if iss_select == "true":
        locations.append("International Space Station")
    if liwa_select == "true":
        locations.append("Liwa")
    if london_select == "true":
        locations.append("London")
    if la_select == "true":
        locations.append("Los Angeles")
    if ny_select == "true":
        locations.append("New York")
    if san_fran_select == "true":
        locations.append("San Francisco")
    if sea_select == "true":
        locations.append("Under the Sea")
    return locations
#set the user perferred video quality
def get_quality():
    quality_download = list()
    if download_quality == "HD":
        quality_download.append("HD")
    elif download_quality == "4K":
        quality_download.append("4K")
    elif download_quality == "Both":
        quality_download.append("HD")
        quality_download.append("4K")
    return quality_download
def listdir(path, files=False):
    dir, file = xbmcvfs.listdir(path)
    if files:
        return file
    else:
        return dir
def validatePath(path):
    #for fixing slash problems.
    #e.g. Corrects 'Z://something' -> 'Z:'
    return xbmc.validatePath(path)
download_folder = validatePath(addon.getSetting("download_folder"))
def file(path, mode=""):
    return xbmcvfs.File(path, mode)
#def creates a list of downloaded videos
def get_local():
    locations = list()
    if download_folder != "":
        try:
            for location in listdir(download_folder):
                locations.append(location)
        except Exception as err:
            pass
    return locations
def exists(path):
    #Check for a file or folder existence
    beta(path)
    return xbmcvfs.exists(path)
def mkdir(path):
    #Create a folder.
    return xbmcvfs.mkdir(path)
def mkpath(path):
    #Make all directories along the path
    return xbmcvfs.mkdirs(path)
#def takes video location and produces a list of video objects
def get_video_data(location=""):
    videos = list()
    #def only gets videos from International Space Station
    def get_iss_videos(location):
        for video in aerial_data[location]["videos"]:
            if video["iss"] == "True":
                videos.append(video)
    def get_sea_videos(location):
        for video in aerial_data[location]["videos"]:
            if video["sea"] == "True":
                videos.append(video)
    #def only gets videos not from ISS
    def get_videos(location):
        for video in aerial_data[location]["videos"]:
            if video["iss"] == "False":
                videos.append(video)


    if "Space Station" in location:
        for location in sorted(aerial_data.keys()):
            get_iss_videos(location)
    elif "Sea" in location:
        for location in sorted(aerial_data.keys()):
            get_sea_videos(location)
    else:
        get_videos(location)
    return videos
def cleanup():
    beta("CLEANUP_DEBUG: Cleaning up from earlier versions")
    rem = os.path.join(cwd, "New Folder")
    t = os.path.join(cwd, "test.py")
    try:
        for i in os.listdir(rem):
            os.remove(os.path.join(rem, i))
    except Exception as err:
        beta("CLEANUP_SUCCESS: Contents removed.")
    try:
        os.chdir(cwd)
    except Exception as err:
        beta("CLEANUP_ERROR: Should be fatal missing main directory!")
    try:
        os.remove(t)
    except Exception as err:
        beta("CLEANUP_SUCCESS: PY removed.")
    try:
        os.rmdir(rem)
    except Exception as err:
        beta("CLEANUP_SUCCESS: Folder removed.")
    return
def time():
    t = datetime.datetime.today()
    data = {
            "day": t.day,
            "week": t.isocalendar()[1],
            "month": t.month
                }
    return data
def update_date(data):
    with open(last_updated, "w") as dump:
        json.dump(data, dump)
