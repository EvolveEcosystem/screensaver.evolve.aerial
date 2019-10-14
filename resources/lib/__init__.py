import ast, common as c, json, local_videos, random, sys, xbmc, xbmcgui, xbmcvfs
from fetcher import get_Videos as gV
from threading import Thread as t

monitor = xbmc.Monitor()
player = xbmc.Player()
playlist = xbmc.PlayList(1)
local = local_videos.Downloader(mode=0)


class Start:
    def __init__(self):
        c.beta("START_CLASS_DEBUG: Starting")
        if player.isPlayingAudio():
            if c.audio_mode() == 1:
                player.stop()
                xbmc.sleep(1)
                self.launch()
            elif c.audio_mode() == 2:
                return
            else:
                while not monitor.abortRequested():
                    c.beta("Monitoring")
                    if not player.isPlayingAudio():
                        c.beta("Audio Stopped")
                        self.launch()
                        return
                if monitor.waitForAbort(15):
                    return
        else:
            self.launch()
    def launch(self):
        self.background = VideoWindow('evolve_screensaver.xml', c.path, 'default', '1080i')
        self.background.doModal()
        del self.background

class Player(xbmc.Player):
    def __init__(self):
        xbmc.Player.__init__(self, xbmc.Player())
    def OnAVChange(self):
        pass

    def onAVStarted(self):
        pass

    def onPlayBackStopped(self):
        self.stop()

    def onPlayBackError(self):
        self.playnext()

class VideoWindow(xbmcgui.WindowXML):
    def __init__(self, *args, **kwargs):
        self.player = Player()
        self.player.showSubtitles(False)
    def onInit(self):
        self.npv = False
        if player.isPlayingVideo():
            if c.video_mode() == 2:
                if bool(xbmc.getCondVisibility("Player.Paused")):
                    self.npT = player.getVideoInfoTag().getTitle()
                    self.npt = player.getTime()
                    self.nptT = player.getTotalTime()
                    self.npv = True
                    self.np()
                    self.launch()
                    self.buildcpi()
                    player.play(self.playlist, listitem=self.lpi)
                    xbmc.sleep(1)
                    player.pause()
                    waiting = True
                    while waiting:
                        if player.isPlayingVideo():
                            player.seekTime(float(int(self.npt)-10))
                            waiting = False
                            self.close()
                        if monitor.waitForAbort(.5):
                            return
                    xbmc.sleep(5)
            return
        else:
            self.launch()
        try:
            del self.overlay
        except:
            pass


    def launch(self):
        self.playlist = xbmc.PlayList(1)
        self.playlist.clear()
        self.videolist = self.getPlaylist()
        global list_len
        list_len = len(self.videolist)
        if len(self.videolist) == 0:
            c.ok("Your \"Time of Day\" selection is {}. The locations you have downloaded do not have any {} Time videos. Please download more locations or change your \"Time of Day\" settings.".format(c.time_of_day.title(), gV().get_current_time().title()))
            return
        random.shuffle(self.videolist)
        for video in self.videolist:
            listitem = xbmcgui.ListItem("%s" % video.get("id"))
            listitem.setInfo( 'video', {
                        'plot': "{}".format(video.get("poi")),
                        'tagline' : "{}".format(video.get("timeOfDay")),
                        'title' : "{}".format(video.get('location'))
                        })
            self.playlist.add(video.get("url"), listitem=listitem)
        self.player.play(self.playlist, windowed=True)
        self.overlay = OverlayWindow('evolve_dialog.xml', c.path, 'default', '1080i')
        self.overlay.doModal()
        if not self.npv:
            if self.overlay.running == False:
                self.close()
    def np(self):
        p = """{
                "jsonrpc": "2.0",
                "method": "Playlist.GetItems",
                "params":
                    { "properties":[
                                      "title",
                                      "artist",
                                      "albumartist",
                                      "genre",
                                      "year",
                                      "rating",
                                      "album",
                                      "track",
                                      "duration",
                                      "comment",
                                      "lyrics",
                                      "musicbrainztrackid",
                                      "musicbrainzartistid",
                                      "musicbrainzalbumid",
                                      "musicbrainzalbumartistid",
                                      "playcount",
                                      "fanart",
                                      "director",
                                      "trailer",
                                      "tagline",
                                      "plot",
                                      "plotoutline",
                                      "originaltitle",
                                      "lastplayed",
                                      "writer",
                                      "studio",
                                      "mpaa",
                                      "cast",
                                      "country",
                                      "imdbnumber",
                                      "premiered",
                                      "productioncode",
                                      "runtime",
                                      "set",
                                      "showlink",
                                      "streamdetails",
                                      "top250",
                                      "votes",
                                      "firstaired",
                                      "season",
                                      "episode",
                                      "showtitle",
                                      "thumbnail",
                                      "file",
                                      "resume",
                                      "artistid",
                                      "albumid",
                                      "tvshowid",
                                      "setid",
                                      "watchedepisodes",
                                      "disc",
                                      "tag",
                                      "art",
                                      "genreid",
                                      "displayartist",
                                      "albumartistid",
                                      "description",
                                      "theme",
                                      "mood",
                                      "style",
                                      "albumlabel",
                                      "sorttitle",
                                      "episodeguide",
                                      "uniqueid",
                                      "dateadded",
                                      "channel",
                                      "channeltype",
                                      "hidden",
                                      "locked",
                                      "channelnumber",
                                      "starttime",
                                      "endtime",
                                      "specialsortseason",
                                      "specialsortepisode",
                                      "compilation",
                                      "releasetype",
                                      "albumreleasetype",
                                      "contributors",
                                      "displaycomposer",
                                      "displayconductor",
                                      "displayorchestra",
                                      "displaylyricist",
                                      "userrating"
                                    ],
                      "playlistid": 1
                     },
                "id": 1
                }"""
        self.np_data = json.loads(xbmc.executeJSONRPC(p))
    def buildcpi(self):
        self.playlist = xbmc.PlayList(1)
        self.playlist.clear()
        for i in self.np_data['result']['items']:
            listitem = xbmcgui.ListItem("%s" % i.get("title"))
            info = {}
            listitem.setLabel("{}".format(i.get("title")))
            listitem.setLabel2("{}".format(i.get("year")))
            listitem.setInfo('video', {
                                    "plot": i.get("plot"),
                                    "tagline" :i.get("tagline"),
                                    "title": i.get("title"),
                                    "year": i.get("year")
                                    })
            listitem.setArt({"thumb": i.get("thumbnail")})
            listitem.setPath(path=i.get('file'))
            self.playlist.add(i.get('file'), listitem=listitem)
            if i.get('title') in self.npT:
                listitem.setProperty("Resume", "{}".format(float(int(self.npt)-10)))
                listitem.setProperty("Total Time", "{}".format(float(int(self.nptT))))
                self.lpi = listitem
    def getPlaylist(self):
        if c.mode == "Stream":
            c.beta("START_CLASS_DEBUG: Getting streaming playlist")
            playlist = gV().stream_playlist()
        else:
            c.beta("START_CLASS_DEBUG: Getting local playlist")
            playlist = gV().local_playlist()
            if "restart" in playlist:
                c.beta("START_CLASS_DEBUG: Just Downloaded first video, restart!")
                playlist = self.getPlaylist()
        c.beta("START_CLASS_DEBUG: We have a playlist returning")
        return playlist

class OverlayWindow(xbmcgui.WindowXMLDialog):
    def __init__(self, *args, **kwargs):
        self.player = Player()
        self.running = True
        self.poi = None
        self.timeOfDay = None
        self.location = None
        self.t = 0
        self.psmmode = ""
        self.file = None
        self.changing = False
        self.displaying = False
        t(target=self.psm).start()

    def onInit(self):
        self.psmkillall = False
        self.label = self.getControl(51)
        self.label2 = self.getControl(52)
        self.label.setLabel(" ")
        self.label2.setLabel(" ")
        while self.running:
            if int(playlist.size()) == (int(playlist.getposition())+1):
                try:
                    if int(self.t) == (int(self.T)-3):
                        self.player.pause()
                        self.changing = True
                        self.file = "REPEATING"
                        self.player.play(playlist, windowed=True)
                except:
                    pass
            if self.player.isPlaying():
                self.n_file = self.player.getPlayingFile()
                if self.changing:
                    self.t = 0
                    self.label.setLabel(" ")
                    if self.file != self.n_file or int(self.player.getTime()) > 1: self.changing = False
                if not self.changing:
                    self.t = int(self.player.getTime())
                    self.T = int(self.player.getTotalTime())
                    self.Et = self.T-10
                    self.data_allocation()
            if self.countdown:
                self.running = False
                self.player.stop()
                c.beta("Video PAused")
                try:
                    c.beta("trying dpms")
                    xbmc.executebuiltin('ToggleDPMS')
                    self.psmmode = "DPMS"
                    self.psmkillall = True
                    player.stop()
                    self.label.setLabel("")
                    self.label2.setLabel("Power saving mode was enabled press back to return.")
                except Exception as err:
                    c.beta("DPMS TOGGLE FAILED")
                    c.beta("{}".format(err))
                    try:
                        xbmc.executebuiltin('CECStandby')
                        c.beta("CEC WORKED")
                        self.psmmode = "CEC"
                        self.psmkillall = True
                        player.stop()
                        self.label.setLabel("")
                        self.label2.setLabel("Power saving mode was enabled press back to return.")
                    except Exception as err:
                        c.beta("CECSTandby Failed")
                        c.beta("Will continue SCREENSAVER")
                        c.beta("{}".format(err))
                        self.psmkillall = False
                if not self.psmkillall:
                    self.player.play(playlist, windowed=True)
                    self.countdown = False
            xbmc.sleep(1000)

    def data_allocation(self):
        if self.n_file != self.file:
            try:
                info = self.player.getVideoInfoTag()
                self.location = info.getTitle()
                self.poi = ast.literal_eval(info.getPlot())
                self.timeOfDay = info.getTagLine()
                self.key_list = list()
                self.file = self.n_file
                self.changing = False
                for i in sorted(self.poi.iterkeys(), key=int):
                    self.key_list.append(i)
            except Exception as err:
                c.beta(err)
        try:
            if self.key_list != "":
                if int(self.t) > int(self.key_list[0]):
                    self.label.setLabel(self.poi["%s" % self.key_list[0]])
                    j = t(target=self.counter)
                    j.start()
                    del self.key_list[0]
        except Exception as err:
            c.log(err)
            try:
                if self.label.getLabel() != self.location:
                    if self.poi == "" or self.poi == None:
                        self.label.setLabel(self.location)
                        j = t(target=self.counter)
                        j.start()
            except:
                pass
        return
    def  psm(self):
        self.countdown = False
        if int(c.psm) > 0:
            countdown = int(c.psm)
            while countdown > 0:
                xbmc.sleep(1000)
                countdown-=1
                self.countdown = False
            self.countdown = True
    def counter(self):
        if not self.displaying:
            self.displaying = True
            for i in range(10):
                if not self.changing:
                    if not self.label.isVisible():
                        self.label.setVisible(True)
                else:
                    self.label.setLabel("")
                    self.label.setVisible(False)
                xbmc.sleep(1000)
        self.label.setVisible(False)
        self.displaying = False
    def onAction(self, action):
        if action == 10 or action == 92:
            self.running = False
            if "CEC" in self.psmmode :
                xbmc.executebuiltin("CECActivateSource")
                c.beta("CECActivateSource")
            elif "DPMS" in self.psmmode:
                xbmc.executebuiltin('ToggleDPMS')
                c.beta("TOGGLE DPMS")
            xbmc.sleep(1000)
            self.player.stop()
            self.close()

        elif action == 100 or action == 103 or action == 7:
            j = t(target=self.counter)
            j.start()
        elif action == 1:
            if int(playlist.size()) == (int(playlist.getposition())+1):
                self.player.pause()
                self.changing = True
                self.file = "REPEATING"
                self.player.play(playlist, windowed=True)
            else:
                self.changing = True
                self.player.playprevious()
        elif action == 2:
            if int(playlist.size()) == (int(playlist.getposition())+1):
                self.player.pause()
                self.changing = True
                self.file = "REPEATING"
                self.player.play(playlist, windowed=True)
            else:
                self.changing = True
                self.player.playnext()



if __name__ == '__main__':
    c.cleanup()
    if len(sys.argv) == 1:
        c.beta("Starting Screensaver from Executable")
        Start()
    elif 'auto' in sys.argv[1]:
        c.beta("Starting Screensaver from Preview or Automatically")
        Start()
    elif 'download' in sys.argv[1]:
        c.beta("DOWNLOAD_DEBUG: User clicked on Manual Download")
        if c.download_folder != "":
            c.beta("DOWNLOAD_DEBUG: User has a download folder set")
            local.download()
        else:
            c.beta("DOWNLOAD_DEBUG: User has not set download folder.")
            c.ok("Please set a Download Location in the General Tab of Settings.")
            c.beta("DOWNLOAD_DEBUG: User has accepted the notification")
