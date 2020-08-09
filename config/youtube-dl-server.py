# ATTENTION: I am not responsible for your download of illegal content or without permission.
#            Please respect the laws license permits of your country.


# --------------- # --------------- # imports # --------------- # --------------- #
from __future__ import unicode_literals

import glob
import json
import os
import random
import subprocess
import sys
import safer
import time
from collections import ChainMap
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from math import pow
from pathlib import Path
from threading import Thread

import libtorrent as lt
from bottle import Bottle, redirect, request, route, run, static_file, view
from extractor import Extractor


# --------------- # --------------- # contfiguration # --------------- # --------------- #
app = Bottle()

app_defaults = {
    'YDL_SERVER_HOST': '0.0.0.0',
    'YDL_SERVER_PORT': 8080,
    'WORKER_COUNT': 4,
    'DOWNLOAD_DIR': "ydl-downloads",
    'LOCAL': False,
    'SUB_PATH': "downloads",
    'SHOW_HIDDEN': False,
    'SWAP': "", # used for testing purpose
    'HISTORY': []
}


# --------------- # --------------- # functions: help # --------------- # --------------- #


# --------------- # help: view download # --------------- #
def constructPath(path):
    '''
    Needed for File Serving
    Convert path to windows path format.
    '''
    if(sys.platform=='win32'):
      return "\\"+path.replace('/','\\')
    return path #Return same path if on linux or unix


# --------------- # help: history append # --------------- #
def addHistory(url, title, kind, status, path):

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    if status == "Started":
        if len(download_history) == 0:
            download_history.append({
                    'url': url,
                    'title': title,
                    'kind': kind,
                    'status': status,
                    'path': path,
                    'timestamp': timestamp,
                })
        else:
            for content, item in enumerate(download_history):
                if (item['kind'] == kind) and (item['title'] == title) and (item['path'] == path):
                    download_history[content] = {
                        'url': url,
                        'title': title,
                        'kind': kind,
                        'status': status,
                        'path': path,
                        'timestamp': timestamp,
                    }
                    return

                download_history.append({
                    'url': url,
                    'title': title,
                    'kind': kind,
                    'status': status,
                    'path': path,
                    'timestamp': timestamp,
                })

    if status == "Finished":
        for content, item in enumerate(download_history):
            if (item['kind'] == kind) and (item['title'] == title) and (item['path'] == path):
                download_history[content] = {
                    'url': url,
                    'title': title,
                    'kind': kind,
                    'status': status,
                    'path': path,
                    'timestamp': timestamp,
                }
                saveHistory()
                return

    if status == "Running":
        for content, item in enumerate(download_history):
            if (item['kind'] == kind) and (item['title'] == title) and (item['path'] == path):
                download_history[content] = {
                    'url': url,
                    'title': title,
                    'kind': kind,
                    'status': status,
                    'path': path,
                    'timestamp': timestamp,
                }
                return

    if status == "Pending":
        for content, item in enumerate(download_history):
            if (item['kind'] == kind) and (item['title'] == title) and (item['path'] == path):
                download_history[content] = {
                    'url': url,
                    'title': title,
                    'kind': kind,
                    'status': status,
                    'path': path,
                    'timestamp': timestamp,
                }
                return

    if status == "Failed":
        for content, item in enumerate(download_history):
            if (item['kind'] == kind) and (item['title'] == title) and (item['path'] == path):
                download_history[content] = {
                    'url': url,
                    'title': title,
                    'kind': kind,
                    'status': status,
                    'path': path,
                    'timestamp': timestamp,
                }
                saveHistory()
                return

    # saveHistory()

    # print("history.1 url: " + url)
    # print("history.2 title: " + title)
    # print("history.3 kind: " + kind)
    # print("history.4 status: " + status)
    # print("history.5 path: " + path)
    # print("history.6 history: " + str(download_history))


# --------------- # help: load history entries # --------------- #
def loadHistory():
    try:

        filename = sourcePath + "/logs/history.txt"
        swapList = []

        if not os.path.isfile(filename):
            os.makedirs(filename.rsplit("/",1)[0])
            historyLog = open(filename, "w")
            historyLog.writelines("# History Log: " + datetime.now().strftime("%Y-%m-%d_%H-%M-%S"))
            historyLog.close()

        with safer.open(filename, "r") as f:

            swap = f.readline()
            while swap != "":

                if "#" in swap:
                    swap = f.readline()
                    continue

                if swap == "":
                    swap = f.readline()
                    continue

                url, title, kind, status, path, timestamp = swap.split(";")
                swapList.append({
                    'url': url,
                    'title': title,
                    'kind': kind,
                    'status': status,
                    'path': path,
                    'timestamp': timestamp,
                })
                swap = f.readline()

            if len(swapList)>10:
                return swapList[-9:]
            else:
                return swapList[-(len(swapList)-1):]

    except:
        print("Failure at loadHistory. Error: " + str(sys.exc_info()[0]))


# --------------- # help: load history-log # --------------- #
def loadLog():
    try:

        filename = sourcePath + "/logs/history.txt"
        swapList = []

        if not os.path.isfile(filename):
            os.makedirs(filename.rsplit("/",1)[0])
            historyLog = open(filename, "w")
            historyLog.writelines("# History Log: " + datetime.now().strftime("%Y-%m-%d_%H-%M-%S"))
            historyLog.close()

        with safer.open(filename, "r") as f:

            swap = f.readline()
            while swap != "":

                if "#" in swap:
                    swap = f.readline()
                    continue

                if swap == "":
                    swap = f.readline()
                    continue

                url, title, kind, status, path, timestamp = swap.split(";")
                swapList.append({
                    'url': url,
                    'title': title,
                    'kind': kind,
                    'status': status,
                    'path': path,
                    'timestamp': timestamp,
                })
                swap = f.readline()

            return swapList

    except:
        print("Failure at loadLog. Error: " + str(sys.exc_info()[0]))


# --------------- # help: check history and log # --------------- #
def checkHistory():
    try:

        compareList = loadLog()

        for i in download_history:

            # if the status is not Finished or Failed, next Item
            if (i['status'] != "Finished") or (i['status'] != "Failed"):
                continue

            for j in compareList:

                # if item history is identical to compareList next
                if (i['title'] == j['title']) and (i['path'] == j['path']) and (i['kind'] == j['kind']) and (i['status'] == j['status']):
                    continue
                else:
                    compareList.append(i)

                print("compareList: " + str(compareList))

        # compareList == Logfile with new Items
        return compareList

    except:
        print("Failure at checkHistory. Error: " + str(sys.exc_info()[0]))


# --------------- # help: write to log # --------------- #
def saveHistory():
    try:

        logHistory = checkHistory()

        filename = sourcePath + "/logs/history.txt"

        if not os.path.isfile(filename):
            os.makedirs(filename.rsplit("/",1)[0])
            historyLog = open(filename, "w")
            historyLog.write("# History Log: " + datetime.now().strftime("%Y-%m-%d_%H-%M-%S\n"))
            historyLog.close()

        with safer.open(filename, 'w') as historyLog:

            historyLog.writelines("# History Log: " + datetime.now().strftime("%Y-%m-%d_%H-%M-%S\n"))

            for item in logHistory:
                print("item" + str(item))
                print("saved item was: " + str(item))
                historyLog.writelines("{url};{title};{kind};{status};{path};{timestamp};".format(url=item['url'], title=item['title'], kind=item['kind'],status=item['status'], path=item['path'], timestamp=item['timestamp']))
    except:
        print("Failure at saveHistory. Error: " + str(sys.exc_info()[0]))


# --------------- # --------------- # functions: app # --------------- # --------------- #


# --------------- # view: home # --------------- #
@app.route('/')
@view('index')
def serv_ui():
    return {}


# --------------- # view: history # --------------- #
@app.route('/history')
@view('history')
def server_history():

    display_history = []

    if len(download_history)>10:
        display_history = download_history[-9:]
    else:
        display_history = download_history[-(len(download_history)-1):]

    return {
        "history": display_history,
    }


# --------------- # view: downloads # --------------- #
@app.route('/downloads/<filename:re:.*>') #match any string after /
@view('download')
def server_download(filename):

    if not workPath in str(app_vars['SWAP']):
        app_vars['SWAP'] = workPath

    path = str(app_vars['SWAP']) + "/" + constructPath(filename)
    webpage = []

    # Serving File
    if (os.path.isfile(path)):
        if (os.path.split(path)[-1][0] == '.' and show_hidden == False): #Allow accessing hidden files?

            app_vars['SWAP'] = os.getcwd()
            os.chdir(sourcePath)
            return "404! Not found.<br /> Allow accessing hidden files?"

            if path.rsplit('.',1)[1] in formats:
                return redirect("/view")

        return static_file(constructPath(filename), root = workPath)  #serve a file

    # Serving Directory
    else:
        try:
            os.chdir(path)

            for x in glob.glob('*'):

                if (x == os.path.split(__file__)[-1]) or ((x[0] == '.') and (show_hidden == False)):  #Show hidden files?
                    continue

                #get the scheme of the requested url
                scheme = request.urlparts[0]
                #get the hostname of the requested url
                host = request.urlparts[1]

                #just html formatting :D
                if filename == "":
                    html = scheme + "://" + host + sub + "/" + x
                else:
                    html = scheme + "://" + host + sub + "/" + filename + "/" + x

                webpage.append({
                    "url": html,
                    "title": x,
                })

        except Exception as e:  #Actually an error accessing the file or switching to the directory

            app_vars['SWAP'] = os.getcwd()
            os.chdir(sourcePath)
            return "404! Not found.<br /> Actually an error accessing the file or switching to the directory"

    os.chdir(sourcePath)
    return { "downloads": webpage, }


# --------------- # static # --------------- #
@app.route('/static/:filename#.*#')
def server_static(filename):
    return static_file(filename, root='./static')


# --------------- # api: add # --------------- #
# api download
@app.route('/api/add', method='POST')
def addToQueue():
    url = request.forms.get("url")
    title = request.forms.get("title")
    tool = request.forms.get("downloadTool")
    path = workPath + "/" + request.forms.get("path")

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

    # ---

    if tool == "youtube-dl":
        download_executor.submit(download_ydl, url, title, path, parameters)

    if tool == "wget":
        download_executor.submit(download_wget, url, path, parameters)

    if tool == "torrent":
        download_executor.submit(download_torrent, url, path, parameters)

    print("Added url " + url + " to the download queue")

    return redirect("/")


# --------------- # api: update # --------------- #
@app.route("/update", method="GET")
def update():
    command = ["pip", "install", "--upgrade", "youtube-dl"]
    proc = subprocess.Popen(
        command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    output, error = proc.communicate()
    return {
        "output": output.decode('ascii'),
        "error":  error.decode('ascii')
    }

# --------------- # --------------- # functions: download # --------------- # --------------- #
# these try catch blocks, because this functions are threaded


# --------------- # download: youtube-dl # --------------- #
def download_ydl(url, title, path, parameters):

    try:
        ydl, url, title = extractor.preProcessor(url, title, path, parameters)

        # ---

        addHistory(url, title, "youtube-dl", "Started", path)

        # ---

        i = 0
        returned_value = ""

        while i < 3:
            print("try: " + str(i+1))

            addHistory(url, title, "youtube-dl", "Running", path)
            returned_value = os.system(ydl)

            if returned_value > 0:
                i += 1

                addHistory(url, title, "youtube-dl", "Pending", path)
                timer = random.randint(200,1000)/100
                time.sleep(timer)

                if i >= 3:
                    addHistory(url, title, "youtube-dl", "Failed", path)
                    return
            else:
                addHistory(url, title, "youtube-dl", "Finished", path)
                return

    except KeyboardInterrupt:
        pass
    except:
        addHistory(url, title, "youtube-dl", "Failed", path)
        print("Failure at Youtube-dl. Error: " + str(sys.exc_info()[0]))


# --------------- # download: wget # --------------- #
def download_wget(content, path, parameters):

    try:
        wget = "wget -c -P {path} {url}".format(path = path, url = content)

        if parameters[3] != "":
            wget = wget + " --limit-rate={}".format(parameters[3]+"M")

        # ---

        addHistory(content, content.rsplit('/',1)[1], "wget", "Started", path)

        # ---

        i = 0
        returned_value = ""

        while i < 3:
            print("try: " + str(i+1))

            addHistory(content, content.rsplit('/',1)[1], "wget", "Running", path)
            returned_value = os.system(wget)

            if returned_value > 0:
                i += 1

                addHistory(content, content.rsplit('/',1)[1], "wget", "Pending", path)
                timer = random.randint(200,1000)/100
                time.sleep(timer)

                if i >= 3:
                    addHistory(content, content.rsplit('/',1)[1], "wget", "Failed", path)
                    return
            else:
                addHistory(content, content.rsplit('/',1)[1], "wget", "Finished", path)
                return

    except KeyboardInterrupt:
        pass
    except:
        addHistory(content, content.rsplit('/',1)[1], "wget", "Failed", path)
        print("Failure at wget. Error: " + str(sys.exc_info()[0]))

# --------------- # download: torrent # --------------- #
def download_torrent(content, path, parameters):

    try:
        dTime = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

        addHistory(content, dTime, "torrent", "Started", path)

        # ---

        limit = 0

        if parameters[3] != "":
            limit = int(round(parameters[3] * pow(1024, 2)))

        params = { 'save_path': path }

        # ---

        try:
            handler = lt.add_magnet_uri(torrentSession, content, params)
            handler.set_download_limit(limit)
            torrentSession.start_dht()

            addHistory(content, dTime, "torrent", "Running", path)

            print("downloading metadata...")
            while (not handler.has_metadata()):
                time.sleep(1)
            print("got metadata, starting torrent download...")
            while (handler.status().state != lt.torrent_status.seeding):
                s = handler.status()
                state_str = ['queued', 'checking', 'downloading metadata', \
                    'downloading', 'finished', 'seeding', 'allocating']
                print('%.2f%% complete (down: %.1f kb/s up: %.1f kB/s peers: %d) %s' % \
                    (s.progress * 100, s.download_rate / 1024, s.upload_rate / 1024, \
                    s.num_peers, state_str[s.state]))
                time.sleep(5)

            addHistory(content, dTime, "torrent", "Finished", path)
        except:
            addHistory(content, dTime, "torrent", "Failed", path)

    except KeyboardInterrupt:
        pass
    except:
        addHistory(content, dTime, "torrent", "Failed", path)
        print("Failure at torrent. Error: " + sys.exc_info()[0])

# ---

# def get_ydl_options(request_options):
#     ydl_vars = ChainMap(os.environ, app_defaults)

#     # List of all options can be found here:
#     # https://github.com/ytdl-org/youtube-dl/blob/master/youtube_dl/options.py
#     return {
#         'format': ydl_vars['YDL_FORMAT'],
#         'outtmpl': ydl_vars['YDL_OUTPUT_TEMPLATE'],
#         'download_archive': ydl_vars['YDL_ARCHIVE_FILE'],
#         'writesubtitles': True,  # --write-sub
#         'allsubtitles': True,  # --all-subs
#         'ignoreerrors': True,  # --ignore-errors
#         'continue_dl': False,  # --no-continue
#         'nooverwrites': True,  # --no-overwrites
#         'addmetadata': True,  # --add-metadata
#         'writedescription': True,  # --write-description
#         'writeinfojson': True,  # --write-info-json
#         'writeannotations': True,  # --write-annotations
#         'writethumbnail': True,  # --write-thumbnail
#         'embedthumbnail': True,  # --embed-thumbnail
#         'subtitlesformat': "srt",  # --sub-format "srt"
#         'embedsubtitles': True,  # --embed-subs
#         'merge_output_format': "mkv",  # --merge-output-format "mkv"
#         'recodevideo': "mkv",  # --recode-video "mkv"
#         'embedsubtitles': True  # --embed-subs
#     }


# --------------- # --------------- # main # --------------- # --------------- #
if __name__ == "__main__":

    app_vars = ChainMap(os.environ, app_defaults)


    # --------------- # folder # --------------- #
    if bool(app_vars['LOCAL']):
        workPath = os.getcwd()
        sourcePath = os.getcwd()
    else:
        workPath = "/tmp/" + str(app_vars['DOWNLOAD_DIR'])
        sourcePath = "/usr/src/youtube-dl-server/run"

    print("Creating Download Folder: " + workPath)
    if not os.path.exists(workPath):
        os.makedirs(workPath)


    # --------------- # file browser # --------------- #
    print("Loading: File Browser")
    show_hidden = bool(app_vars['SHOW_HIDDEN'])
    sub = "/" + str(app_vars['SUB_PATH'])
    app_vars['SWAP'] = workPath

    # View Formats
    formats = ['mp4']


    # --------------- # modul: extractor # --------------- #
    print("Loading: Extractors")
    extractor = Extractor.getInstance()


    # --------------- # modul: torrent # --------------- #
    print("Loading: Torrent")
    torrentSession = lt.session()


    # --------------- # youtube-dl # --------------- #
    print("Updating youtube-dl to the newest version")
    updateResult = update()
    print(updateResult["output"])
    print(updateResult["error"])


    # --------------- # threads # --------------- #
    print("Started download, thread count: " + str(app_vars['WORKER_COUNT']))

    download_executor = ThreadPoolExecutor(max_workers = (int(app_vars['WORKER_COUNT'])+1))


    # --------------- # history # --------------- #
    download_history = loadHistory()


    # --------------- # app # --------------- #
    app.run(host=app_vars['YDL_SERVER_HOST'],
            port=app_vars['YDL_SERVER_PORT'],
            debug=True)
