from datetime import datetime
import glob
import os
import subprocess
from concurrent.futures import ThreadPoolExecutor
from time import sleep

from bottle import Bottle, redirect, request, route, run, static_file, view, TEMPLATE_PATH

import your_dl_server.downloader as downloader
import your_dl_server.ioutils as ioutils
import your_dl_server.extractor as extractor
import your_dl_server.server_history as server_history
from your_dl_server.dto import dto


class Server:
    def __init__ (self, host, port, worker, dir, local, hidden):
        self._app = Bottle()
        self._host = host
        self._port = port
        self._route()

        self.dto = dto()

        self.local = local
        self.hidden = hidden

        self.pathSub = '/downloads'
        self.pathWork = ''
        self.pathSource = ''
        self.pathLog = ''
        self.pathSwap = ''
        
        self.downloadDir = dir
        self.downloadExecutor = ThreadPoolExecutor(max_workers = (int(worker)+1))


    def setup(self):
        if bool(self.local):
            self.pathWork = os.getcwd() + '/' + self.downloadDir
            self.pathSource = os.getcwd()
            self.pathLog = os.getcwd() + "/logs"
        else:
            self.pathWork = "/tmp/" + self.downloadDir
            self.pathSource = self.dto.getPathToRoot()
            self.pathLog = "/tmp/logs"

        if not os.path.exists(self.pathLog):
            self.dto.publishLoggerInfo("Creating Folder Log: " + self.pathLog)
            os.makedirs(self.pathLog)

        self.dto.setLogPath(self.pathLog)
        sleep(1)
        self.dto.publishLoggerInfo("Setting Logger: " + self.pathLog)

        if not os.path.isfile(self.pathLog + "/history.txt"):
            self.dto.publishLoggerInfo("Creating Log File: " + self.pathLog + "/history.txt")
            historyLog = open(self.pathLog + "/history.txt", "w")
            historyLog.writelines("# History Log: " + datetime.now().strftime("%Y-%m-%d_%H-%M-%S"))
            historyLog.close()

        if not os.path.exists(self.pathWork):
            self.dto.publishLoggerInfo("Creating Folder Download: " + self.pathWork)
            os.makedirs(self.pathWork)



    def start(self):
        path = os.path.join(self.dto.getPathToRoot(), 'views')
        self.dto.publishLoggerDebug('server set Template Path: ' + path)
        TEMPLATE_PATH.insert(0, path)
        self._app.run(host=self._host, port=self._port, debug=self.dto.getLogging())


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

        display_logHistory = server_history.loadHistory(self.dto, 'history')
        display_downloads = []

        if len(display_logHistory)>10:
            display_logHistory = display_logHistory[-10:]
        else:
            display_logHistory = display_logHistory


        # list of current running downloads
        if len(self.dto.getDownloadList())>10:
            display_downloads = self.dto.getDownloadList()[-10:]
        else:
            display_downloads = self.dto.getDownloadList()

        return {
            "history": display_logHistory,
            "display_downloads": display_downloads,
        }


    @view('download')
    def serve_download(self, filename):

        if not self.pathWork in self.pathSwap:
            self.pathSwap = self.pathWork

        if filename == '':
            path = self.pathSwap
        else:
            path = self.pathSwap + "/" + ioutils.constructPath(filename)
            
        directories = []
        files = []

        # Serving File
        if (os.path.isfile(path)):
            if (os.path.split(path)[-1][0] == '.' and not self.hidden): # Allow accessing hidden files?

                self.pathSwap = os.getcwd()
                os.chdir(self.pathSource)
                return "404! Not found.<br /> Allow accessing hidden files?"

            # if path.rsplit('.',1)[1] in formats:
            #     return redirect("/view")

            return static_file(ioutils.constructPath(filename), root = self.pathWork)  # serve a file

        # Serving Directory
        else:
            try:
                os.chdir(path)

                for x in glob.glob('*'):

                    if (x == os.path.split(__file__)[-1]) or ((x[0] == '.') and not self.hidden):  # Show hidden files?
                        continue

                    #get the scheme of the requested url
                    scheme = request.urlparts[0]
                    #get the hostname of the requested url
                    host = request.urlparts[1]

                    if filename == "":
                        html = scheme + "://" + host + self.pathSub + "/" + x
                    else:
                        html = scheme + "://" + host + self.pathSub + "/" + filename + "/" + x

                    if os.path.isfile(path + "/" + x):
                        files.append({
                            "url": html,
                            "title": x,
                        })

                    if os.path.isdir(path + "/" + x):
                        directories.append({
                            "url": html,
                            "title": x,
                        })


            except Exception as e:  #Actually an error accessing the file or switching to the directory

                self.pathSwap = os.getcwd()
                os.chdir(self.pathSource)
                return "404! Not found.<br /> Actually an error accessing the file or switching to the directory"


        os.chdir(self.pathSource)
        self.dto.publishLoggerDebug("directories: " + str(directories) + " | files: " + str(files))
        return { "directories": directories, 'files': files }


    def serve_static(self, filename):
        path = os.path.join(self.dto.getPathToRoot(), 'static')
        return static_file(filename, root=path)


    def addToQueue(self):
        url = request.forms.get("url")
        title = request.forms.get("title")
        tool = request.forms.get("downloadTool")

        cookie = request.forms.get("cookie")
        linkList = request.forms.get("list").splitlines()

        path = self.pathWork
        if request.forms.get("path") != '':
            path = os.path.join(self.pathWork, request.forms.get("path"))

        parameter = '--continue'
        if request.forms.get("retries") != '':
            parameter += ' --retries {}', request.forms.get("retries")

        if request.forms.get("minSleep") != '':
            parameter += ' --min-sleep-interval {}', request.forms.get("minSleep")

        if request.forms.get("maxSleep") != '':
            parameter += ' --max-sleep-interval {}', request.forms.get("maxSleep")

        parameters = [
            request.forms.get("username"),
            request.forms.get("password"),
        ]

        if not url and not linkList:
            return {"success": False, "error": "/q called without a 'url' query param"}


        # Prepare Data
        content = url + ';' + title + ';' + request.forms.get('reference') + ';' + path

        bandwidth = request.forms.get("bandwidth")
        if bandwidth != '':
            if not bandwidth[-1].isalpha():
                self.dto.setBandwidth(bandwidth + 'M')
            else:
                self.dto.setBandwidth(bandwidth)

        self.dto.setExternalDownloader(request.forms.get("download"))


        # URL Serperation
        if 'magnet:?' in url:
            tool = "torrent"

        if tool == "youtube-dl":
            if url != '':
                self.downloadExecutor.submit(extractor.ydl_extractor, self.dto, content)
            else:
                for item in linkList:
                    self.downloadExecutor.submit(extractor.ydl_extractor, self.dto, item)

        if tool == "aria2":
            if url != '':
                self.downloadExecutor.submit(downloader.download_aria2, self.dto, content, path)
            else:
                self.downloadExecutor.submit(downloader.download_aria2_dnc, self.dto, linkList, path)

        if tool == "wget":
            if url != '':
                self.downloadExecutor.submit(downloader.download_wget, self.dto, url, '', '')
            else:
                for item in linkList:
                    self.downloadExecutor.submit(downloader.download_wget, self.dto, url, '', '')


        if tool == "torrent":
            if url != '':
                self.downloadExecutor.submit(downloader.download_aria2_magnet, self.dto, url, path)
            else:
                for item in linkList:
                    self.downloadExecutor.submit(downloader.download_aria2_dnc, self.dto, linkList, path)
                    pass

        self.dto.publishLoggerInfo("Added url " + url + " to the download queue")

        return redirect("/")


    def update(self):
        command = ["pip", "install", "--upgrade", "youtube-dl"]
        proc = subprocess.Popen(
            command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        output, error = proc.communicate()

        self.dto.publishLoggerDebug(output.decode('ascii'))
        self.dto.publishLoggerError(error.decode('ascii'))
