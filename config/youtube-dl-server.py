# ATTENTION: This is only a example of to use a python bind of torrent library in Python for educational purposes.
#            I am not responsible for your download of illegal content or without permission.
#            Please respect the laws license permits of your country.

from __future__ import unicode_literals

import json
import os
import random
import subprocess
import glob
import sys
import time
from collections import ChainMap
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from queue import Queue
from threading import Thread
import libtorrent as lt

from bottle import Bottle, redirect, request, route, run, static_file, debug, view
import bottle
from extractor import Extractor
from math import pow

app = Bottle()

app_defaults = {
    'YDL_SERVER_HOST': '0.0.0.0',
    'YDL_SERVER_PORT': 8080,
    'WORKER_COUNT': 4,
    'DOWNLOAD_DIR': "ydl-downloads",
    'LOCAL': "run",
    'SUB_PATH': "downloads",
    'SHOW_HIDDEN': False,
}

# --------------- #

def constructPath(path):
    '''
    Needed for File Serving
    Convert path to windows path format.
    '''
    if(sys.platform=='win32'):
        return "\\"+path.replace('/','\\')
    return path #Return same path if on linux or unix

# --------------- #

@app.route('/')
@view('index')
def serve_ui():
    # return static_file('index.html', root = str(app_vars['LOCAL']) + "/")
    return

    # ---

@app.route('/history')
@view('history')
def serve_history():
    # return static_file('index.html', root = str(app_vars['LOCAL']) + "/")
    return {
        "history": download_history,
    }

    # ---

@app.route('/static/:filename#.*#')
def serve_static(filename):
    return static_file(filename, root = str(app_vars['LOCAL']) + "/static")

    # ---

@app.route('/downloads/<filename:re:.*>') #match any string after /
def serve_download(filename):
    path = "/tmp/" + str(app_vars['DOWNLOAD_DIR']) + "/" + constructPath(filename)

    html = '''<html>
                <head><title>downloads</title>
                    <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.1.3/css/bootstrap.min.css" integrity="sha384-MCw98/SFnGE8fJT3GXwEOngsV7Zt27NXFoaoApmYm81iuXoPkFOJwJ8ERdknLPMO" crossorigin="anonymous">
                    <style>
                    </style>
                </head>
                <body>
                    <!-- Optional JavaScript -->
                    <!-- jQuery first, then Popper.js, then Bootstrap JS -->
                    <script src="https://code.jquery.com/jquery-3.3.1.slim.min.js" integrity="sha384-q8i/X+965DzO0rT7abK41JStQIAqVgRVzpbzo5smXKp4YfRvH+8abtTE1Pi6jizo" crossorigin="anonymous"></script>
                    <script src="https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.14.3/umd/popper.min.js" integrity="sha384-ZMP7rVo3mIykV+2+9J3UJ46jBk0WLaUAdn689aCwoqbBJiSnjAK/l8WvCWPIPm49" crossorigin="anonymous"></script>
                    <script src="https://stackpath.bootstrapcdn.com/bootstrap/4.1.3/js/bootstrap.min.js" integrity="sha384-ChfqqxuZUCnJSK3+MXmPNIyE6ZbWh2IMqE241rYiqJxyMiZ6OW/JmZQ5stwEULTy" crossorigin="anonymous"></script>
                
                <div class="container d-flex flex-column text-light text-center">
                <br>
                <div class = "row justify-content-center">
                    <div class = "col-6"><a href = "/" target=""><button class="btn btn-primary">Youtube-dl UI</button></a></div>
                    <div class = "col-6"><a onclick="history.back()"><button class="btn btn-primary">Previous Folder</button></a></div>
                </div>
                <div class="jumbotron bg-transparent flex-grow-1">
                <table border=0>'''

    # Serving File
    if (os.path.isfile(path)):
        if (os.path.split(path)[-1][0] == '.' and show_hidden == False): #Allow accessing hidden files?
            return "404! Not found.<br /> Allow accessing hidden files?"
        return static_file(constructPath(filename), root = "/tmp/" + str(app_vars['DOWNLOAD_DIR']) + "/")  #serve a file
    
    # Serving Directory
    else:
        try:
            os.chdir(path)
            for x in glob.glob('*'):
                if (x == os.path.split(__file__)[-1]) or ((x[0] == '.') and (show_hidden == False)):  #Show hidden files?
                    continue

                #get the scheme of the requested url
                scheme = bottle.request.urlparts[0]
                #get the hostname of the requested url
                host = bottle.request.urlparts[1]

                #just html formatting :D
                if filename == "":
                    html = html + "<td><a href = '" + scheme + "://" + host + sub + "/" + x +"'>" + x + "</a><td></tr>"
                else:
                    html = html + "<td><a href = '" + scheme + "://" + host + sub + "/" + filename + "/" + x +"'>" + x + "</a><td></tr>"
        except Exception as e:  #Actually an error accessing the file or switching to the directory
            html = "404! Not found.<br /> Actually an error accessing the file or switching to the directory"

    return html+"</table><hr><br><br></div></div></body></html>" #Append the remaining html code

    # ---

@app.route('/api/add', method='POST')
def addToQueue():
    url = request.forms.get("url")
    title = request.forms.get("title")
    tool = request.forms.get("downloadTool")
    path = "/tmp/" + str(app_vars['DOWNLOAD_DIR']) + "/" + request.forms.get("path")

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

    # -----

@app.route("/update", method="GET")
def update():
    command = ["pip", "install", "--upgrade", "youtube-dl"]
    proc = subprocess.Popen(command, stdout = subprocess.PIPE, stderr = subprocess.PIPE)

    output, error = proc.communicate()
    return {
        "output": output.decode('ascii'),
        "error":  error.decode('ascii')
    }

# --------------- #

def download_ydl(url, title, path, parameters):

    ydl = extractor.preProcessor(url, title, path, parameters)

    download_history.append({
        "url": extractor.url,
        "title": extractor.title
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

# -----

def download_wget(content, path, parameters):
    
    wget = "wget -c --random-wait -P {path}/ {url}".format(path = path, url = content)

    if parameters[3] != "":
        wget = wget + " --limit-rate={}".format(parameters[3]+"M")

    # ---

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

# -----

def download_torrent(content, path, parameters):
    limit = 0

    if parameters[3] != "":
        limit = int(round(parameters[3] * pow(1024, 2)))
    
    params = { 'save_path': path }

    # ---

    handler = lt.add_magnet_uri(torrentSession, content, params)
    handler.set_download_limit(limit)
    torrentSession.start_dht()

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

    print("finished: torrent")

# --------------- #

if __name__ == "__main__":

    app_vars = ChainMap(os.environ, app_defaults)
    
    # --- Creating Folder
    
    dir = "/tmp/" + str(app_vars['DOWNLOAD_DIR'])
    print("Creating Download Folder: " + dir)
    if not os.path.exists(dir):
        os.makedirs(dir)

    # --- File Browser

    print("Loading: File Browser")
    show_hidden = bool(app_vars['SHOW_HIDDEN'])
    sub = "/" + str(app_vars['SUB_PATH'])

    # --- Extractor Modul

    print("Loading: Extractors")
    extractor = Extractor.getInstance()

    # --- Torrent Modul

    print("Loading: Torrent")
    torrentSession = lt.session()

    # --- Youtube-dl Server

    print("Updating youtube-dl to the newest version")
    updateResult = update()
    print(updateResult["output"])
    print(updateResult["error"])

    print("Started download, thread count: " + str(app_vars['WORKER_COUNT']))

    download_executor = ThreadPoolExecutor(max_workers = (int(app_vars['WORKER_COUNT'])+1))
    download_history = []

    app.run(    
                host = app_vars['YDL_SERVER_HOST'], 
                port = app_vars['YDL_SERVER_PORT'], 
                debug = True,
                #reloader=True
            )
