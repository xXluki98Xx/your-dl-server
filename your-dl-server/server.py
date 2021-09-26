import os
import subprocess
from concurrent.futures.thread import ThreadPoolExecutor

from bottle import Bottle, redirect, request, route, run, static_file, view

import downloader
import server_history


class Server:
    def __init__ (self, dto, host, port, worker, dir, local, subpath, hidden):
        self._app = Bottle()
        self._host = host
        self._port = port
        self._debug = dto.getLogging()
        self._route()

        self.dto = dto

        self.local = local
        self.hidden = hidden

        self.pathSub = subpath
        self.pathWork = ''
        self.pathSource = ''
        self.pathLog = ''
        self.pathSwap = ''
        
        self.downloadDir = dir
        self.downloadList = []
        self.downloadExecutor = ThreadPoolExecutor(max_workers = (int(worker)+1))


    def setup(self):
        if bool(self.local):
            self.pathWork = os.getcwd()
            self.pathSource = os.getcwd()
            self.pathLog = os.getcwd() + "/logs"
        else:
            self.pathWork = "/tmp/" + self.downloadDir
            self.pathSource = "/usr/src/youtube-dl-server/run"
            self.pathLog = "/tmp/logs"

        self.dto.publishLoggerInfo("Creating Download Folder: " + self.pathWork)
        if not os.path.exists(self.pathWork):
            os.makedirs(self.pathWork)

    # Routes
    def _route(self):
        self._app.route('/', method='GET', callback=self.serve_ui)
        self._app.route('/history', method='GET', callback=self.serve_history)
        self._app.route('/downloads/<filename:re:.*>', method='GET', callback=self.serve_download) #match any string after /
        self._app.route('/static/:filename#.*#', method='GET', callback=self.serve_static)
        self._app.route('/api/add', method='POST', callback=self.addToQueue)
        self._app.route('/update', method='GET', callback=self.update)


    # Viewes
    @view('index')
    def serve_ui(self):
        return {}

    @view('history')
    def serve_history(self):

        display_logHistory = server_history.loadHistory()
        display_downloads = []

        if len(display_logHistory)>10:
            display_logHistory = display_logHistory[-10:]
        else:
            display_logHistory = display_logHistory


        # list of current running downloads
        if len(self.downloadList)>10:
            display_downloads = self.downloadList[-10:]
        else:
            display_downloads = self.downloadList

        return {
            "history": display_logHistory,
            "display_downloads": self.downloadList,
        }


    @view('download')
    def serve_download(self, filename):

        if not self.pathWork in self.pathSwap:
            self.pathSwap = self.pathWork

        path = self.pathSwap + "/" + constructPath(filename)
        webpage = []

        # Serving File
        if (os.path.isfile(path)):
            if (os.path.split(path)[-1][0] == '.' and not self.hidden): #Allow accessing hidden files?

                self.pathSwap = os.getcwd()
                os.chdir(self.pathSource)
                return "404! Not found.<br /> Allow accessing hidden files?"

                if path.rsplit('.',1)[1] in formats:
                    return redirect("/view")

            return static_file(constructPath(filename), root = self.pathWork)  #serve a file

        # Serving Directory
        else:
            try:
                os.chdir(path)

                for x in glob.glob('*'):

                    if (x == os.path.split(__file__)[-1]) or ((x[0] == '.') and not self.hidden):  #Show hidden files?
                        continue

                    #get the scheme of the requested url
                    scheme = request.urlparts[0]
                    #get the hostname of the requested url
                    host = request.urlparts[1]

                    #just html formatting :D
                    if filename == "":
                        html = scheme + "://" + host + self.pathSub + "/" + x
                    else:
                        html = scheme + "://" + host + self.pathSub + "/" + filename + "/" + x

                    webpage.append({
                        "url": html,
                        "title": x,
                    })

            except Exception as e:  #Actually an error accessing the file or switching to the directory

                self.pathSwap = os.getcwd()
                os.chdir(self.pathSource)
                return "404! Not found.<br /> Actually an error accessing the file or switching to the directory"

        os.chdir(self.pathSource)
        return { "downloads": webpage, }


    def serve_static(self, filename):
        return static_file(self, filename, root='./static')


    def addToQueue(self):
        url = request.forms.get("url")
        title = request.forms.get("title")
        tool = request.forms.get("downloadTool")
        path = self.pathWork + "/" + request.forms.get("path")

        parameters = [
            request.forms.get("retries"),
            request.forms.get("minSleep"),
            request.forms.get("maxSleep"),
            request.forms.get("bandwidth"),
            request.forms.get("download"),
            request.forms.get("username"),
            request.forms.get("password"),
            request.forms.get("reference")
        ]

        if not url:
            return {"success": False, "error": "/q called without a 'url' query param"}

        # --- # URL Serperation

        if 'magnet:?' in url:
            tool = "torrent"

        if tool == "youtube-dl":
            self.download_executor.submit(downloader.download_ydl, url, title, path, parameters)

        if tool == "wget":
            self.download_executor.submit(downloader.download_wget, self.dto, url, path, parameters)

        if tool == "torrent":
            self.download_executor.submit(downloader.download_aria2c_magnet, self.dto, url, path)

        self.dto.publishLoggerInfo("Added url " + url + " to the download queue")

        return redirect("/")


    def update(self):
        command = ["pip", "install", "--upgrade", "youtube-dl"]
        proc = subprocess.Popen(
            command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        output, error = proc.communicate()

        self.dto.publishLoggerInfo(output.decode('ascii'))
        self.dto.publishLoggerDebug(error.decode('ascii'))
