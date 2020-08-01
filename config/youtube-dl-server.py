# ATTENTION: This is only a example of to use a python bind of torrent library in Python for educational purposes.
#            I am not responsible for your download of illegal content or without permission.
#            Please respect the laws license permits of your country.

# ---------- # imports # ---------- #

from __future__ import unicode_literals

import glob
import json
import os
import random
import subprocess
import sys
import time
from collections import ChainMap
from concurrent.futures import ThreadPoolExecutor
from math import pow
from pathlib import Path
from threading import Thread

# import libtorrent as lt
from bottle import Bottle, redirect, request, route, run, static_file, view
from extractor import Extractor

# ---------- # instantiation # ---------- #

app = Bottle()

# ---------- # configuration # ---------- #

app_defaults = {
    'YDL_SERVER_HOST': '0.0.0.0',
    'YDL_SERVER_PORT': 8080,
    'WORKER_COUNT': 4,
    'DOWNLOAD_DIR': "ydl-downloads",
    'LOCAL': False,
    'SUB_PATH': "downloads",
    'SHOW_HIDDEN': False,
    'SWAP': "", # used for testing purpose
}

# ---------- # help functions # ---------- #

def constructPath(path):
    '''
    Needed for File Serving
    Convert path to windows path format.
    '''
    if(sys.platform=='win32'):
        return "\\"+path.replace('/','\\')
    return path #Return same path if on linux or unix

# ---------- # routing # ---------- #

# view home
@app.route('/')
@view('index')
def serv_ui():
    return {}

# ---

# view history
@app.route('/history')
@view('history')
def serv_history():
    return {
        "history": download_history,
    }

# ---

# view downloads
@app.route('/downloads/<filename:re:.*>') #match any string after /
@view('download')
def server_download(filename):
    path = str(app_vars['SWAP']) + "/" + constructPath(filename)
    webpage = []

    # Serving File
    if (os.path.isfile(path)):
        if (os.path.split(path)[-1][0] == '.' and show_hidden == False): #Allow accessing hidden files?
            
            app_vars['SWAP'] = os.getcwd()
            os.chdir(sourcePath)
            return "404! Not found.<br /> Allow accessing hidden files?"
 
        return static_file(constructPath(filename), root = sourcePath)  #serve a file
    
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

# ---------- # serving static # ---------- #

@app.route('/static/:filename#.*#')
def server_static(filename):
    return static_file(filename, root='./static')

# ---------- # api calls # ---------- #

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

    # if tool == "torrent":
    #     download_executor.submit(download_torrent, url, path, parameters)

    print("Added url " + url + " to the download queue")

    return redirect("/")

# ---

# api update youtube-dl
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

# ---------- # downloader # ---------- #

# content audio video
def download_ydl(url, title, path, parameters):

    ydl, url, title = extractor.preProcessor(url, title, path, parameters)

    print(url)
    print(title)

    download_history.append({
        "url": url,
        "title": title,
        "kind": "youtube-dl"
    })

    # ---

    i=0
    returned_value = ""

    while i < 3:

        print()
        returned_value = os.system(ydl)

        if returned_value > 0:
            i += 1
            timer = random.randint(200,1000)/100
            print("sleep for " + str(timer) + "s")
            time.sleep(timer)

        if i == 3:
            print("This was the Command: \n%s" % ydl)
            return returned_value
        else:
            return returned_value

    print("finished: youtube-dl")

# ---

# content wget
def download_wget(content, path, parameters):
    
    wget = "wget -c --random-wait -P {path}/{url}".format(path = path, url = content)

    if parameters[3] != "":
        wget = wget + " --limit-rate={}".format(parameters[3]+"M")

    # ---

    download_history.append({
        "url": content,
        "title": content.rsplit('/',1)[1],
        "kind": "wget",
    })

    i=0
    returned_value = ""

    while i < 3:

        print()
        returned_value = os.system(wget)

        if returned_value > 0:
            i += 1
            timer = random.randint(200,1000)/100
            print("sleep for " + str(timer) + "s")
            time.sleep(timer)

            if i == 3:
                print("This was the Command: \n%s" % wget)
                return returned_value
            else:
                return returned_value

    print("finished: wget")

# ---
# content torrent magnetlink
# def download_torrent(content, path, parameters):
#     limit = 0

#     if parameters[3] != "":
#         limit = int(round(parameters[3] * pow(1024, 2)))
    
#     params = { 'save_path': path }

#     # ---

#     handler = lt.add_magnet_uri(torrentSession, content, params)
#     handler.set_download_limit(limit)
#     torrentSession.start_dht()

#     print("downloading metadata...")
#     while (not handler.has_metadata()):
#         time.sleep(1)
#     print("got metadata, starting torrent download...")
#     while (handler.status().state != lt.torrent_status.seeding):
#         s = handler.status()
#         state_str = ['queued', 'checking', 'downloading metadata', \
#                 'downloading', 'finished', 'seeding', 'allocating']
#         print('%.2f%% complete (down: %.1f kb/s up: %.1f kB/s peers: %d) %s' % \
#                 (s.progress * 100, s.download_rate / 1024, s.upload_rate / 1024, \
#                 s.num_peers, state_str[s.state]))
#         time.sleep(5)

#     print("finished: torrent")

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

# ---------- # app start # ---------- #

if __name__ == "__main__":

    app_vars = ChainMap(os.environ, app_defaults)

    # --- Creating Folder

    if bool(app_vars['LOCAL']):
        workPath = os.getcwd()
        sourcePath = os.getcwd()
    else:
        workPath = "/tmp/" + str(app_vars['DOWNLOAD_DIR'])
        soucrePath = "/usr/src/youtube-dl-server/run"

        print("Creating Download Folder: " + workPath)
        if not os.path.exists(workPath):
            os.makedirs(workPath)

    # --- File Browser

    print("Loading: File Browser")
    show_hidden = bool(app_vars['SHOW_HIDDEN'])
    sub = "/" + str(app_vars['SUB_PATH'])
    app_vars['SWAP'] = workPath

    # --- Extractor Modul

    print("Loading: Extractors")
    extractor = Extractor.getInstance()

    # # --- Torrent Modul

    # print("Loading: Torrent")
    # torrentSession = lt.session()

    # # --- Youtube-dl Server

    print("Updating youtube-dl to the newest version")
    updateResult = update()
    print(updateResult["output"])
    print(updateResult["error"])

    print("Started download, thread count: " + str(app_vars['WORKER_COUNT']))

    download_executor = ThreadPoolExecutor(max_workers = (int(app_vars['WORKER_COUNT'])+1))
    download_history = []

    app.run(host=app_vars['YDL_SERVER_HOST'],
            port=app_vars['YDL_SERVER_PORT'], 
            debug=True)
