import common as c, local_videos, json, xbmc
monitor = xbmc.Monitor()
localize = local_videos.Downloader(mode=2)

if __name__ == '__main__':
    c.beta("SERVICE_DEBUG: Has Started")
    while not monitor.abortRequested():
        c.beta("SERVICE_DEBUG: Mode is {}".format(c.mode))
        if "Local" in c.mode:
            if c.download_folder:
                c.beta("SERVICE_DEBUG: Has download folder")
                c.beta("SERVICE_DEBUG: DLF {}".format(c.download_folder))
                try:
                    data = json.load(open(c.last_updated))
                    day = data.get("day")
                    week = data.get("week")
                    month = data.get("month")
                    c.beta("SERVICE_DEBUG: Last Updated {}".format(data))
                except:
                    c.beta("SERVICE_DEBUG: First Run")
                    c.beta("SERVICE_DEBUG: Download Frequency is {}".format(c.download_time))
                    day = 0
                    week = 0
                    month = 0
                if "Daily" in c.download_time:
                    d = c.time()['day']
                    if int(day) < d or (int(day)>28 and d == 1):
                        localize.download()
                if "Week" in c.download_time:
                    w = c.time()['week']
                    if int(week) < w:
                        localize.download()
                if "Month" in c.download_time:
                    m = c.time()['month']
                    if int(month) < m:
                        localize.download()
        c.beta("SERVICE_DEBUG: Waiting")    
    # Sleep/wait for abort for 1 hour
        if monitor.waitForAbort(3600):
            # Abort was requested while waiting. We should exit
            c.beta("SERVICE_DEBUG: Has Stopped")
            break
