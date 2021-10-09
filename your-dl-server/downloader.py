import os
import random
import shutil
import subprocess
import sys
import time

import functions
import ioutils
import server_history


# ----- # ----- #
def getEchoList(stringList):
    listString = ''
    for item in stringList:
        if item.startswith('#') or item == '':
            continue
        listString +=('%s\n' % item)
    return listString


# ----- # ----- #
def download_wget(dto, content, accept, reject):
    dto.publishLoggerDebug('download wget')

    try:
        if ';' in content:
            swap = content.split(';')
            content = swap[0]
            directory = swap[1]
            title = swap[2]
        else:
            directory = ''
            title = ''

        path = os.path.join(os.getcwd(),directory)

        wget = 'wget -c -w 5 --random-wait --limit-rate={bw} -e robots=off'.format(bw = dto.getBandwidth())

        if directory != '':
            wget += ' -P {dir}'.format(dir = path)

        if title != '':
            wget += ' -O {title}'.format(title = ioutils.getTitleFormated(title))

        if accept != '':
            wget += ' --accept {extention}'.format(extention = accept)

        if reject != '':
            wget += ' --reject {extention}'.format(extention = reject)

        # --no-http-keep-alive --no-clobber

        if dto.getSync():
            wget = wget + ' -r -N -np -nd -nH'

        wget += ' "{url}"'.format(url = content)

        # file count
        path, dirs, files = next(os.walk(path))
        file_count_prev = len(files)

        # dir size
        dirSize = subprocess.check_output(['du','-s', path]).split()[0].decode('utf-8')

        # free storage
        freeStorage = shutil.disk_usage(path).free

        try:
            # file size
            fileSize = subprocess.getoutput('wget "' + content + '" --spider --server-response -O - 2>&1| sed -ne "/Content-Length/{s/.*: //;p}"')
            testSize = int(fileSize)
        except:
            testSize = dirSize

        dto.publishLoggerDebug('wget command: ' + wget)

        if (int(freeStorage) >= int(testSize)):

            download(dto, wget, 'wget', content, [content, title, directory])

        else:
            dto.publishLoggerWarn('wget - not enough space')
            dto.publishLoggerWarn('Directory size: ' + ioutils.bytes2human(int(dirSize)*1000))
            dto.publishLoggerWarn('free Space: ' + ioutils.bytes2human(freeStorage))

            if dto.getSpace():
                functions.func_removeFiles(dto, path, file_count_prev)
            return 507

    except KeyboardInterrupt:
        dto.publishLoggerDebug('Interupt by User')
        dto.publishLoggerError('Plattform: wget | Content: ' + content)
        os._exit(1)

    except:
        dto.publishLoggerError('wget - error at download: ' + str(sys.exc_info()))


def download_ydl(dto, content, parameters, output, stringReferer, infos):
    if dto.getBandwidth() != '0':
        parameters += ' --limit-rate {}'.format(dto.getBandwidth())

    if dto.getAxel():
        parameters += ' --external-downloader axel'

        if dto.getBandwidth() != '0':
            parameters += ' --external-downloader-args "-s {}"'.format(ioutils.human2bytes(dto.getBandwidth()))

    if stringReferer != '':
        parameters += ' --referer "{reference}"'.format(reference = stringReferer)

    if dto.getVerbose():
        parameters += ' --verbose'

    dl = 'youtube-dl {parameter} {output} "{url}"'.format(parameter = parameters, output = output, url = content)

    dto.publishLoggerDebug('download ydl: ' + dl)

    return download(dto, dl, 'ydl', content, infos)


def download_aria2c(dto, content):
    if ';' in content:
        swap = content.split(';')
        content = swap[0]
        directory = swap[1]
    else:
        directory = ''

    if ('magnet:?xt=urn:btih' in content):
        return download_aria2c_magnet(dto, content, directory)

    dl = 'aria2c -x 8 -j 16 --continue --min-split-size=1M --optimize-concurrent-downloads "{}" '.format(content)

    if dto.getBandwidth() != '0':
        dl += ' --max-overall-download-limit={}'.format(dto.getBandwidth())

    if directory != '':
        dl += ' --dir="{}"'.format(directory)

    dto.publishLoggerDebug('download aria2c: ' + dl)

    return download(dto, dl, 'aria2c', content, [content, content.rsplit('/', 1)[1], directory])


def download_aria2c_dnc(dto, content, directory):
    links = getEchoList(content)

    dl = 'echo ' + links + ' | '

    dl += 'aria2c -i - -x 8 -j 16 --continue --min-split-size=1M --optimize-concurrent-downloads'

    if dto.getBandwidth() != '0':
        dl += ' --max-overall-download-limit={}'.format(dto.getBandwidth())

    if directory != '':
        dl += ' --dir="{}"'.format(directory)

    dto.publishLoggerDebug('download aria2c: ' + dl)

    return download(dto, dl, 'aria2c', content, [content, ioutils.getTitleFormated(''), directory])


def download_aria2c_magnet(dto, content, dir):
    dl = 'aria2c --seed-time=0'

    if dir != '':
        dl += ' --dir="{}"'.format(dir)

    if dto.getBandwidth() != '0':
        dl += ' --max-overall-download-limit={}'.format(dto.getBandwidth())

    dl += ' "{}"'.format(content)

    return download(dto, dl, 'aria2c-magnet', content, [content, ioutils.getTitleFormated(''), dir])


def download(dto, command, platform, content, infos):
    try:
        dto.publishLoggerDebug(platform + ' command is: ' + command)

        if dto.getServer():
            server_history.addHistory(dto, infos[0], infos[1], platform, "Started",  infos[2])

        i = 0
        returned_value = ''

        while i < dto.getRetries():
            if dto.getServer():
                server_history.addHistory(dto, infos[0], infos[1], platform, "Running",  infos[2])

            returned_value = os.system('echo \'' + command + '\' >&1 | bash')

            if returned_value > 0:
                if returned_value == 2048:
                    return returned_value
                else:
                    dto.publishLoggerDebug('Error Code: ' + str(returned_value))
                    i += 1

                    if dto.getServer():
                        server_history.addHistory(dto, infos[0], infos[1], platform, "Pending",  infos[2])


                    timer = random.randint(200,1000)/100
                    dto.publishLoggerInfo('sleep for ' + str(timer) + 's')
                    time.sleep(timer)

                    if i == dto.getRetries():
                        if dto.getServer():
                            server_history.addHistory(dto, infos[0], infos[1], platform, "Failed",  infos[2])


                        dto.publishLoggerWarn('the Command was: %s' % command)
                        dto.publishLoggerError(platform + ' - error at downloading: ' + content)

                        return returned_value

            else:
                if dto.getServer():
                    server_history.addHistory(dto, infos[0], infos[1], platform, "Finished",  infos[2])

                return returned_value


    except KeyboardInterrupt:
        dto.publishLoggerDebug('Interupt by User')
        dto.publishLoggerError('Plattform: ' + platform + ' | Content: ' + content)
        os._exit(1)

    except:
        dto.publishLoggerError(platform + ' - error at downloading: ' + str(sys.exc_info()))
