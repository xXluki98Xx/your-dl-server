import os
import random
import sys
from datetime import datetime

import downloader
import ioutils


def wget(dto, wget, accept, reject):
    repeat = True

    while repeat:
        if wget != '':
            for item in wget:
                if os.path.isfile(item):
                    wget_list(dto, item, accept, reject)
                else:
                    downloader.download_wget(dto, item, accept, reject)

            wget = ''
            ioutils.elapsedTime(dto)

        else:
            try:
                url = input('\nPlease enter the Url:\n')
                dto.setTimeStart(datetime.now())
                downloader.download_wget(dto, url, accept, reject)

            except KeyboardInterrupt:
                pass
        
        if dto.getSingle():
            repeat = False
            break
        
        try:
            answer = input('\nDo you wish another Turn? (y | n):\n')
            if ('y' in answer) :
                repeat = True
                wget = ''
            else:
                repeat = False

        except KeyboardInterrupt:
            repeat = False


# ----- # ----- #
def wget_list(dto, itemList, accept, reject):
    urlList = ioutils.openfile(dto, itemList)
    urlCopy = urlList.copy()

    if dto.getSync():
        random.shuffle(urlList)

    for item in urlList:

        dto.publishLoggerDebug('wget list: ' + str(urlList))

        try:
            if item.startswith('#') or item == '':
                urlCopy.remove(item)
                continue

            dto.publishLoggerDebug('downloading: ' + str(item))

            if dto.getSync():
                downloader.download_wget(dto, str(item), accept, reject)
                dto.publishLoggerInfo('finished: ' + str(item))
            else:
                if downloader.download_wget(dto, str(item), accept, reject) == 0:
                    urlCopy.remove(item)
                    dto.publishLoggerDebug('removed: ' + str(item) + ' | rest list ' + str(urlCopy))

        except KeyboardInterrupt:
            if not dto.getSync():
                ioutils.savefile(dto, itemList, urlCopy, 'wget')

            dto.publishLoggerWarn('Interupt by User')
            ioutils.elapsedTime(dto)
            os._exit(1)

        except:
            dto.publishLoggerError('wget - error at list: ' + str(sys.exc_info()))

        finally:
            # will always be executed last, with or without exception
            if not dto.getSync():
                ioutils.savefile(dto, itemList, urlCopy, 'wget')

    ioutils.elapsedTime(dto)