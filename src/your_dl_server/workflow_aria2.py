import os
import random
import sys
from datetime import datetime

import your_dl_server.downloader as downloader
import your_dl_server.ioutils as ioutils


def aria2(dto, url):
    repeat = True

    while repeat:
        if url != '':
            for item in url:
                if os.path.isfile(item):
                    aria2_list(dto, item)
                else:
                    downloader.download_aria2(dto, item)

            url = ''
            ioutils.elapsedTime(dto)

        else:
            try:
                url = input('\nPlease enter the Url:\n')
                dto.setTimeStart(datetime.now())
                downloader.download_aria2(dto, url)

            except KeyboardInterrupt:
                pass
        
        if dto.getSingle():
            repeat = False
            break
        
        try:
            answer = input('\nDo you wish another Turn? (y | n):\n')
            if ('y' in answer) :
                repeat = True
                url = ''
            else:
                repeat = False

        except KeyboardInterrupt:
            repeat = False


# ----- # ----- #
def aria2_list(dto, itemList):
    urlList = ioutils.openfile(dto, itemList)
    urlCopy = urlList.copy()

    if dto.getSync():
        random.shuffle(urlList)

    for item in urlList:

        dto.publishLoggerDebug('aria2 list: ' + str(urlList))

        try:
            if item.startswith('#') or item == '':
                urlCopy.remove(item)
                continue

            dto.publishLoggerDebug('downloading: ' + str(item))

            if dto.getSync():
                downloader.download_aria2(dto, str(item))
                dto.publishLoggerInfo('finished: ' + str(item))
            else:
                if downloader.download_aria2(dto, str(item)) == 0:
                    urlCopy.remove(item)
                    dto.publishLoggerDebug('removed: ' + str(item) + ' | rest list ' + str(urlCopy))

        except KeyboardInterrupt:
            if not dto.getSync():
                ioutils.savefile(dto, itemList, urlCopy, 'aria2_list')

            dto.publishLoggerWarn('Interupt by User')
            ioutils.elapsedTime(dto)
            os._exit(1)

        except:
            dto.publishLoggerError('aria2 - error at list: ' + str(sys.exc_info()))

        finally:
            # will always be executed last, with or without exception
            if not dto.getSync():
                ioutils.savefile(dto, itemList, urlCopy, 'aria2_list')

    ioutils.elapsedTime(dto)