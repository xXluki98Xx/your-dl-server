from datetime import datetime
import re
import sys
import time
import urllib.request
import os
import subprocess
import youtube_dl
from bottle import unicode


# --------------- # --------------- # class singleton # --------------- # --------------- #
class Extractor:
    __instance = None
    @staticmethod

    def getInstance():
        if Extractor.__instance == None:
            Extractor()
            return Extractor.__instance

    def __init__(self):
        if Extractor.__instance != None:
            raise Exception("This class is a singleton!")
        else:
            Extractor.__instance = self

        self.content = ""
        self.url = ""

        self.title = ""
        self.path = ""
        self.username = ""
        self.password = ""
        self.retries = ""
        self.minSleep = ""
        self.maxSleep = ""
        self.bandwidth = ""
        self.axel = ""
        self.reference = ""

        self.output = ""

# --------------- # --------------- # functions: # --------------- # --------------- #


# --------------- # help: var reset # --------------- #
    def defaultValues(self):
        self.content = ""
        self.url = ""

        self.title = ""
        self.path = ""
        self.username = ""
        self.password = ""
        self.retries = "5"
        self.minSleep = "2"
        self.maxSleep = "15"
        self.bandwidth = ""
        self.axel = ""
        self.reference = ""

        self.output = ""


# --------------- # function: preparation for use # --------------- #
    def preProcessor(self, content, title, path, parameters):
        self.defaultValues()

        # -----

        self.content = content
        self.url = content

        self.title = title

        # -----

        self.retries, self.minSleep, self.maxSleep, self.bandwidth, self.axel, self.username, self.password, self.reference = parameters

        # -----

        if self.retries == "":
            self.retries = "5"

        if self.minSleep == "":
            self.minSleep = "2"

        if self.maxSleep == "":
            self.maxSleep = "15"

        # -----

        if path == "":
            self.path = "."
        else:
            self.path = path

        # -----

        self.parameters = ""
        self.parameters = "--retries {retries} --min-sleep-interval {mins} --max-sleep-interval {maxs} -c".format(retries = self.retries, mins = self.minSleep, maxs = self.maxSleep)

        # -----

        if self.bandwidth == "0":
            pass
        elif self.bandwidth == "":
            pass
        else:
            self.parameters = self.parameters + " --limit-rate {}".format(self.bandwidth)

        # -----

        if self.axel == "axel":
            self.parameters = self.parameters + " --external-downloader axel"

        return self.extraction()


# --------------- # function: url switch # --------------- #
    def extraction(self):

        # provider: streaming...
        if ("fruithosted" in self.content) : return self.host_fruithosted()
        elif ("oloadcdn" in self.content) : return self.host_oloadcdn()
        elif ("verystream" in self.content) : return self.host_verystream()
        elif ("vidoza" in self.content) : return self.host_vidoza()
        elif ("vivo" in self.content) : return self.host_vivo()

        # provider: communities
        elif ("udemy" in self.content) : return self.host_udemy()
        elif ("anime-on-demand" in self.content) : return self.host_animeondemand()
        elif ("wakanim" in self.content) : return self.host_wakanim()
        elif ("vimeo" in self.content) : return self.host_vimeo()
        elif ("cloudfront" in self.content) : return self.host_cloudfront()

        # provider: ...
        elif ("animeholics" in self.content) : return self.host_animeholics()
        elif ("haho.moe" in self.content) : return self.host_hahomoe()
        elif ("sxyprn" in self.content) : return self.host_sxyprn()
        elif ("porngo" in self.content) : return self.host_porngo()
        elif ("xvideos" in self.content) : return self.host_xvideos()

        else : return self.host_default()


# --------------- # function: ydl command # --------------- #
    def download_ydl(self):
        ydl = 'youtube-dl {parameter} {output} {url}'.format(parameter = self.parameters, output = self.output, url = self.url)

        return [ydl, self.url, self.title]

# --------------- # function: title style # --------------- #
    def getTitle(self, oldTitle):
        newTitle = ""

        if self.title == "":
            if oldTitle == "":
                now = datetime.now()
                newTitle = "download_ydl" + now.strftime("%m-%d-%Y_%H-%M-%S")
            else:
                newTitle = oldTitle
        else:
            newTitle = self.title

        newTitle = newTitle.casefold().replace(" ", "-").replace("_","-").replace(".","")

        while newTitle.endswith('-'):
            newTitle = newTitle[:-1]

        while newTitle.startswith('-'):
            newTitle = newTitle[1:]

        self.title = newTitle
        return newTitle

# --------------- # function: title from webpage # --------------- #
    def getTitleWebpage(self):
        req = urllib.request.Request(self.content, headers = {"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req) as response:
            webpage = response.read()

        titleRegex = re.compile('<title>(.*?)</title>')
        m = titleRegex.search(str(webpage))
        if m:
            title = m.group(1)
        print(title)
        return title


# --------------- # --------------- # Extractors # --------------- # --------------- #
# some functions are similar, but in case there is an change at the hoster, you can find and modify it this way better


# --------------- # --------------- # Extractors: streaming... # --------------- # --------------- #
# --------------- # extractors: default # --------------- #
    def host_default(self):
        ydl_opts = {'outtmpl': unicode('%(title)s'),'restrictfilenames':True,'forcefilename':True}

        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(self.url, download=False)
            filename = ydl.prepare_filename(info)

        filename = self.getTitle(filename)

        self.output = '-f best -o "{path}/{title}.%(ext)s"'.format(path = self.path, title = filename)
        return self.download_ydl()


# --------------- # extractors: fruithosted # --------------- #
    def host_fruithosted(self):
        title = self.getTitle("")

        self.output = '-f best -o "{path}/{title}.%(ext)s"'.format(title = title, path = self.path)
        return self.download_ydl()


# --------------- # extractors: openload # --------------- #
    def host_oloadcdn(self):
        title = self.getTitle("")

        self.output = '-f best -o "{path}/{title}.%(ext)s"'.format(title = title, path = self.path)
        return self.download_ydl()


# --------------- # extractors: verystream # --------------- #
    def host_verystream(self):
        title = self.getTitle("")

        self.output = '-f best -o "{path}/{title}.%(ext)s"'.format(title = title, path = self.path)
        return self.download_ydl()


# --------------- # extractors: vidoza # --------------- #
    def host_vidoza(self):
        title = self.getTitle("")

        self.output = '-f best -o "{path}/{title}.%(ext)s"'.format(title = title, path = self.path)
        return self.download_ydl()


# --------------- # extractors: vivo # --------------- #
    def host_vivo(self):
        title = self.getTitle("")

        self.output = '-f best -o "{path}/{title}.%(ext)s"'.format(title = title, path = self.path)
        return self.download_ydl()


# --------------- # --------------- # Extractors: communities # --------------- # --------------- #


# --------------- # extractors: udemy # --------------- #
    def host_udemy(self):
        self.parameter = "--username " + self.username + " --password " + self.password + " " + self.parameters

        title = self.content.split('/',4)[4].rsplit('/',5)[0]
        self.url = "https://www.udemy.com/" + title

        print("media url: " + self.url)

        self.title = title
        self.output = "-f best -o '{path}/%(playlist)s - {title}/%(chapter_number)s-%(chapter)s/%(playlist_index)s-%(title)s.%(ext)s'".format(title = title, path = self.path)
        return self.download_ydl()


# --------------- # extractors: animeondemand # --------------- #
# work in progress
    def host_animeondemand(self):
        self.parameter = "--username " + self.username + " --password " + self.password + " " + self.parameters

        if "www." not in self.url:
            swap = self.url.split('/', 2)
            self.url = "https://www." + swap[2]

        self.output = "-f 'best[format_id*=ger-Dub]' -o '{path}/%(playlist)s/episode-%(playlist_index)s.%(ext)s'".format(path = self.path)
        return self.download_ydl()


# --------------- # extractors: wakanim # --------------- #
# work in progress
    def host_wakanim(self):
        self.parameter = "--username " + self.username + " --password " + self.password + " " + self.parameters

        if "www." not in self.url:
            swap = self.url.split('/', 2)
            self.url = "https://www." + swap[2]

        self.output = "-f 'best[format_id*=ger-Dub]' -o '{path}/%(playlist)s/episode-%(playlist_index)s.%(ext)s'".format(path = self.path)
        return self.download_ydl()


# --------------- # extractors: crunchyroll # --------------- #
    def host_crunchyroll(self):
        self.parameter = "--username " + self.username + " --password " + self.password + " " + self.parameters

        if "www." not in self.url:
            swap = self.url.split('/', 2)
            self.url = "https://www." + swap[2]

        self.output = "-f 'best[format_id*=ger-Dub]' -o '{path}/%(playlist)s/episode-%(playlist_index)s.%(ext)s'".format(path = self.path)
        return self.download_ydl()


# --------------- # extractors: vimeo # --------------- #
# need reference link, if it is embeded
    def host_vimeo(self):
        title = self.getTitle("")

        self.output = '--referer {reference} -f best -o "{path}/{title}.%(ext)s"'.format(reference = self.reference, title = title, path = self.path)
        return self.download_ydl()


# --------------- # extractors: cloudfront # --------------- #
    def host_cloudfront(self):
        title = self.getTitle("")

        self.output = '-f best -o "{path}/{title}.mp4"'.format(title = title, path = self.path)
        return self.download_ydl()


# --------------- # --------------- # Extractors: ... # --------------- # --------------- #


# --------------- # extractors: animeholics # --------------- #
# not longer in maintained
    def host_animeholics(self):
        url = self.content
        webpage = ""

        req = urllib.request.Request(url, headers = {"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req) as response:
            webpage = response.read()

        self.url = str(webpage)[str(webpage).find("https://filegasm.com/watch/"):int(str(webpage).find("https://filegasm.com/watch/"))+43]

        x = re.search('/\d/$|/s\d/$', self.content)
        if x:
            serie = self.content.rsplit('/',1)[0].rsplit('/',2)[1]
            episode = self.content.rsplit('/',1)[0].rsplit('/',2)[2]
        else:
            serie = self.content.rsplit('/',1)[0].rsplit('/',1)[1]
            episode = self.content.rsplit('/',1)[1]

        title = (serie + "-" + episode)
        title = self.getTitle(title)

        self.output = '-f best -o "{path}/{title}.%(ext)s"'.format(title = title, path = self.path)
        return self.download_ydl()


# --------------- # extractors: animeholics # --------------- #
# new site
    def host_hahomoe(self):
        webpage=""

        req = urllib.request.Request(self.content, headers = {"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req) as response:
            webpage = response.read()

        urlRegex = re.compile('<source src="(.*?)" type="video/mp4"></source>')
        m = urlRegex.search(str(webpage))
        if m:
            self.url = m.group(1)

        self.getTitle(self.getTitleWebpage().rsplit(' ', 4)[0])
        self.output = '-f best -o "{path}/{title}.mp4"'.format(title = self.title, path = self.path)
        return self.download_ydl()

# --------------- # extractors: hanime # --------------- #
# doesnt work
    def host_hanime(self):
        title = self.content.rsplit('?',1)[0].rsplit('/',1)[1]

        title = self.getTitle(title)

        self.output = '-f best -o "{path}/{title}.%(ext)s"'.format(title = title, path = self.path)
        return self.download_ydl()


# --------------- # extractors: sxyprn # --------------- #
    def host_sxyprn(self):
        title = self.getTitleWebpage()

        if "#" in title:
            title = title.split('#',1)[0]

        title = self.getTitle(title.rsplit('-', 1)[0])

        self.title = title
        self.output = '-f best -o "{path}/{title}.%(ext)s"'.format(title = title, path = self.path)
        return self.download_ydl()


# --------------- # extractors: xvideos # --------------- #
    def host_xvideos(self):
        title = self.content.rsplit("/",1)[1]

        title = self.getTitle(title)

        self.output = '-f best -o "{path}/{title}.mp4"'.format(title=title, path = self.path)
        return self.download_ydl()


# --------------- # extractors: porngo # --------------- #
    def host_porngo(self):
        title = self.content.rsplit('/',1)[0].rsplit('/',1)[1]

        self.title = title
        self.output = '-f best -o "{path}/{title}.%(ext)s"'.format(title=title, path = self.path)
        return self.download_ydl()