import os
import sys
from datetime import datetime

import safer

from dto import dto


# ----- # ----- #
def addHistory(dto, url, title, kind, status, path):

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    downloadList = dto.getDownloadList()

    if status == "Started":

        # if donwload_history == len 0
        if len(downloadList) == 0:
            downloadList.append({
                'url': url,
                'title': title,
                'kind': kind,
                'status': status,
                'path': path,
                'timestamp': timestamp,
            })

            dto.setDownloadList(downloadList)
            saveHistory(dto)
            return


        # if list not len 0
        for content, item in enumerate(downloadList):
            if (item['kind'] == kind) and (item['title'] == title) and (item['path'] == path):
                downloadList[content] = {
                    'url': url,
                    'title': title,
                    'kind': kind,
                    'status': status,
                    'path': path,
                    'timestamp': timestamp,
                }

                dto.setDownloadList(downloadList)
                saveHistory(dto)
                return


        # if content not in list
        downloadList.append({
            'url': url,
            'title': title,
            'kind': kind,
            'status': status,
            'path': path,
            'timestamp': timestamp,
        })

        dto.setDownloadList(downloadList)
        saveHistory(dto)
        return


    if status == "Finished":
        # search for item
        for content, item in enumerate(dto.getDownloadList()):
            if (item['kind'] == kind) and (item['title'] == title) and (item['path'] == path):
                downloadList[content] = {
                    'url': url,
                    'title': title,
                    'kind': kind,
                    'status': status,
                    'path': path,
                    'timestamp': timestamp,
                }

                dto.setDownloadList(downloadList)
                saveHistory(dto)
                return


    if status == "Running":
        # search for item
        for content, item in enumerate(downloadList):
            if (item['kind'] == kind) and (item['title'] == title) and (item['path'] == path):
                downloadList[content] = {
                    'url': url,
                    'title': title,
                    'kind': kind,
                    'status': status,
                    'path': path,
                    'timestamp': timestamp,
                }
                dto.setDownloadList(downloadList)
                return


    if status == "Pending":
        # search for item
        for content, item in enumerate(downloadList):
            if (item['kind'] == kind) and (item['title'] == title) and (item['path'] == path):
                downloadList[content] = {
                    'url': url,
                    'title': title,
                    'kind': kind,
                    'status': status,
                    'path': path,
                    'timestamp': timestamp,
                }

                dto.setDownloadList(downloadList)
                return


    if status == "Failed":
        # search for item
        for content, item in enumerate(downloadList):
            if (item['kind'] == kind) and (item['title'] == title) and (item['path'] == path):
                downloadList[content] = {
                    'url': url,
                    'title': title,
                    'kind': kind,
                    'status': status,
                    'path': path,
                    'timestamp': timestamp,
                }

                dto.setDownloadList(downloadList)
                saveHistory(dto)
                return


    # saveHistory()

    dto.publishLoggerDebug("history.1 url: " + url)
    dto.publishLoggerDebug("history.2 title: " + title)
    dto.publishLoggerDebug("history.3 kind: " + kind)
    dto.publishLoggerDebug("history.4 status: " + status)
    dto.publishLoggerDebug("history.5 path: " + path)
    dto.publishLoggerDebug("history.6 history: " + str(dto.getHistory))


# --------------- # help: load history-log # --------------- #
def loadLog(dto):
    try:

        filename = dto.getLogPath() + "/history.txt"
        swapList = []

        with safer.open(filename, "r") as f:

            swap = f.readline()
            while swap != "":

                if "#" in swap:
                    swap = f.readline()
                    continue

                url, title, kind, status, path, timestamp, nop = swap.split(";")
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
        dto.publishLoggerError("Failure at loadLog. Error: " + str(sys.exc_info()[1]))
        return []


# --------------- # help: load history entries # --------------- #
def loadHistory(dto):
    try:
        filename = dto.getLogPath() + "/history.txt"
        swapList = []

        with safer.open(filename, "r") as f:

            swap = f.readline()
            while swap != "":

                if "#" in swap:
                    swap = f.readline()
                    continue

                url, title, kind, status, path, timestamp, nop = swap.split(";")
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
                return swapList[-10:]
            else:
                return swapList

    except:
        dto.publishLoggerError("Failure at loadHistory. Error: " + str(sys.exc_info()[1]))
        return swapList

# --------------- # help: check history and log # --------------- #
def checkHistory(dto):
    try:

        logList = loadLog(dto)
        checkList = logList.copy()

        downloadList = dto.getDownloadList()
        downloadListCopy = downloadList.copy()

        for i in logList:
            counter = 0
            for j in checkList:
                if ( (i['title'] == j['title']) and (i['path'] == j['path']) and (i['status'] == j['status'])):
                    counter += 1
                    if counter > 1:
                        checkList.remove(j)

        logList = checkList

        for i in downloadListCopy:

            # if the status is not Finished or Failed, next Item
            if (i['status'] == "Finished") or (i['status'] == "Failed"):

                if len(logList) == 0:
                    logList.append(i)
                    # print("current List: " + str(downloadList))
                    # print("log list: " + str(logList))
                    continue

                for j in logList:

                    # print("statement: " + str((i['title'] == j['title']) and (i['path'] == j['path']) and (i['status'] == j['status'])))
                    # print("download item: " + str(i))
                    # print("log item: " + str(j))

                    # if item history is identical to logList next
                    if ( (i['title'] == j['title']) and (i['path'] == j['path']) and (i['status'] == j['status']) ):
                        try:
                            downloadList.remove(i)
                        except:
                            pass
                    else:
                        logList.append(i)
                        # print("current List: " + str(downloadList))
                        # print("log list: " + str(logList))

        downloadListCopy = downloadList.copy()
        # cleanup current downloads
        for i in downloadListCopy:
            if (i['status'] == "Finished") or (i['status'] == "Failed"):
                downloadList.remove(i)

        checkList = logList.copy()

        for i in logList:
            counter = 0
            for j in checkList:
                if ( (i['title'] == j['title']) and (i['path'] == j['path']) and (i['status'] == j['status'])):
                    counter += 1
                    if counter > 1:
                        checkList.remove(j)

        logList = checkList

        dto.setDownloadList(downloadList)

        # compareList == Logfile with new Items
        return logList

    except:
        dto.publishLoggerError("Failure at checkHistory. Error: " + str(sys.exc_info()))


# --------------- # help: write to log # --------------- #
def saveHistory(dto):
    try:

        logHistory = checkHistory(dto)

        filename = dto.getLogPath() + "/history.txt"

        if not os.path.isfile(filename):
            os.makedirs(filename.rsplit("/",1)[0])
            historyLog = open(filename, "w")
            historyLog.write("# History Log: " + datetime.now().strftime("%Y-%m-%d_%H-%M-%S\n"))
            historyLog.close()
            return

        with safer.open(filename, 'w') as historyLog:

            historyLog.writelines("# History Log: " + datetime.now().strftime("%Y-%m-%d_%H-%M-%S\n"))

            for item in logHistory:
            #     print("item" + str(item))
            #     print("saved item was: " + str(item))
                historyLog.writelines("{url};{title};{kind};{status};{path};{timestamp};\n".format(url=item['url'], title=item['title'], kind=item['kind'],status=item['status'], path=item['path'], timestamp=item['timestamp']))

        dto.setDownloadHistory = loadHistory(dto)

    except:
        dto.publishLoggerError("Failure at saveHistory. Error: " + str(sys.exc_info()))
