import os
import sys
from datetime import datetime

import safer

import your_dl_server.extractor as extractor
import your_dl_server.ioutils as ioutils


def ydl(dto, url):
    repeat = True
    
    while repeat:
        if url != '':
            for item in url:
                if os.path.isfile(item):
                    ydl_list(dto, item)
                else:
                    extractor.ydl_extractor(dto, item)

            url = ''
            ioutils.elapsedTime(dto)

        else:
            try:
                url = input('\nPlease enter the Url:\n')
                dto.setTimeStart(datetime.now())
                extractor.ydl_extractor(dto, url)

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


# ----- # ----- # list
def ydl_list(dto, itemList):
    urlList = ioutils.openfile(dto, itemList)
    urlCopy = urlList.copy()

    dto.publishLoggerDebug('youtube-dl')
    dto.publishLoggerDebug('ydl list: ' + str(urlCopy))

    for item in urlList:

        try:
            if item.startswith('#') or item == '':
                urlCopy.remove(item)
                continue

            dto.publishLoggerDebug('current Download: ' + item)

            if dto.getSync():
                extractor.ydl_extractor(dto, str(item))
                dto.publishLoggerDebug('finished: ' + str(item))
            else:
                if extractor.ydl_extractor(dto, str(item)) == 0:
                    urlCopy.remove(item)
                    dto.publishLoggerDebug('removed: ' + str(item) + ' | rest list ' + str(urlCopy))

        except KeyboardInterrupt:
            dto.publishLoggerDebug('Interupt by User')
            if not dto.getSync():
                ioutils.savefile(dto, itemList, urlCopy, 'ydl')

            ioutils.elapsedTime(dto)
            os._exit(1)

        except:
            dto.publishLoggerError('error at ydl list: ' + str(sys.exc_info()))

        finally:
            # will always be executed last, with or without exception
            if not dto.getSync():
                ioutils.savefile(dto, itemList, urlCopy, 'ydl')

    ioutils.elapsedTime(dto)