from __future__ import unicode_literals

import json
import os
import random
import subprocess
import sys
import time
from collections import ChainMap
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from queue import Queue
from threading import Thread

from bottle import Bottle, redirect, request, route, run, static_file, view, template, debug
from extractor import Extractor

app = Bottle()


app_defaults = {
    'YDL_SERVER_HOST': '0.0.0.0',
    'YDL_SERVER_PORT': 8080,
    'WORKER_COUNT': 4,
    'DOWNLOAD_DIR': "ydl-downloads"
}

# --------------- #

@app.route('/')
def dl_ui():
    return static_file('index.html', root='run/')


@app.route('/static/:filename#.*#')
def serve_static(filename):
    return static_file(filename, root='run//static')

@app.route('/api/add', method='POST')
def addToQueue():
    url = request.forms.get("url")
    title = request.forms.get("title")
    path = "/tmp/" + app_vars['DOWNLOAD_DIR'] + "/" + request.forms.get("path")

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

    download_executor.submit(download, url, title, path, parameters)
    print("Added url " + url + " to the download queue")

    return redirect("/")

    # -----

@app.route("/update", method="GET")
def update():
    command = ["pip3", "install", "--upgrade", "youtube-dl"]
    proc = subprocess.Popen(command, stdout = subprocess.PIPE, stderr = subprocess.PIPE)

    output, error = proc.communicate()
    return {
        "output": output.decode('ascii'),
        "error":  error.decode('ascii')
    }

# --------------- #

def download(url, title, path, parameters):

    ydl = extractor.preProcessor(url, title, path, parameters)

    download_history.append({
        "url": extractor.url,
        "title": extractor.title
    })

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

# --------------- #

if __name__ == "__main__":

    app_vars = ChainMap(os.environ, app_defaults)

    extractor = Extractor.getInstance()

#    home = str(app_vars['DOWNLOAD_DIR'])

    print("Updating youtube-dl to the newest version")
    updateResult = update()
    print(updateResult["output"])
    print(updateResult["error"])

    print("Started download, thread count: " + str(app_vars['WORKER_COUNT']))

    download_executor = ThreadPoolExecutor(max_workers = int(app_vars['WORKER_COUNT']))
    download_history = []

    app.run(    
                host = app_vars['YDL_SERVER_HOST'], 
                port = app_vars['YDL_SERVER_PORT'], 
                debug = True,
                #reloader=True
            )
