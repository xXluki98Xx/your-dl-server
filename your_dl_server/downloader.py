import os
import random
import shutil
import subprocess
import sys
import time

import your_dl_server.functions as functions
import your_dl_server.ioutils as ioutils
import your_dl_server.server_history as server_history
import your_dl_server.workflow_tor as workflow_tor

from your_dl_server.shellmanager import ShellManager


# ----- # ----- #
def getEchoList(stringList):
    listString = ''
    for item in stringList:
        if item.startswith('#') or item == '':
            continue
        listString +=('%s\n' % item)
    return listString


# ----- # ----- #
def download_wget(dto, content, params):
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

        wget = 'wget -c -w 5 --random-wait -e robots=off{}'.format(ioutils.getBandwith(dto, 'wget'))

        if directory != '':
            wget += ' -P {dir}'.format(dir = path)

        if title != '':
            wget += ' -O {title}'.format(title = ioutils.getTitleFormated(title))

        if params != '':
            wget += ' {extention}'.format(extention = params)

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
    parameters += ioutils.getBandwith(dto, 'ydl')

    if '.m3u8' not in content:
        parameters += ioutils.getAccelerator(dto)
    else:
        dto.publishLoggerWarn('.m3u8 found in url, ffmpeg handles that one')

    if stringReferer != '':
        parameters += ' --referer "{reference}"'.format(reference = stringReferer)

    if dto.getVerbose():
        parameters += ' --verbose'

    dl = 'yt-dlp {parameter} {output} "{url}"'.format(parameter = parameters, output = output, url = content)

    dto.publishLoggerDebug('download ydl: ' + dl)

    return download(dto, dl, 'ydl', content, infos)


def download_aria2(dto, content):
    if ';' in content:
        swap = content.split(';')
        content = swap[0]
        directory = swap[1]
    else:
        directory = ''

    if ('magnet:?xt=urn:btih' in content):
        return download_aria2_magnet(dto, content, directory)

    dl = 'aria2c {} {} "{}"'.format(ioutils.getExternalDownloaderDefaults(dto), ioutils.getBandwith(dto, 'aria2'), content)

    if directory != '':
        dl += ' --dir="{}"'.format(directory)

    dto.publishLoggerDebug('download aria2: ' + dl)

    return download(dto, dl, 'aria2', content, [content, content.rsplit('/', 1)[1], directory])


def download_aria2_dnc(dto, content, directory):
    links = getEchoList(content)

    dl = 'echo "' + links + '" | '

    dl += 'aria2c -i - {} {}'.format(ioutils.getExternalDownloaderDefaults(dto), ioutils.getBandwith(dto, 'aria2'))

    if directory != '':
        dl += ' --dir="{}"'.format(directory)

    dto.publishLoggerDebug('download aria2: ' + dl)

    return download(dto, dl, 'aria2', content, [content, ioutils.getTitleFormated(''), directory])


def download_aria2_magnet(dto, content, dir):
    dl = 'aria2c --seed-time=0'

    if dir != '':
        dl += ' --output="{}"'.format(dir)

    dl += ' {} {} "{}"'.format(ioutils.getExternalDownloaderDefaults(dto), ioutils.getBandwith(dto, 'aria2'), content)

    return download(dto, dl, 'aria2-magnet', content, [content, ioutils.getTitleFormated(''), dir])


def download(dto, command, platform, content, infos):

    dto.publishLoggerDebug('platform: ' + platform + ' | command is: ' + command)

    if dto.getServer():
        server_history.addHistory(dto, infos[0], infos[1], platform, "Started",  infos[2])

    # if not dto.getDownloadLegacy():
    #     if 'aria2' in platform:
    #         command += ' --console-log-level=info'

    #     if 'wget' in platform:
    #         command += ' -q --show-progress 2>&1'

    #     if 'ydl' in platform:
    #         command += ' --newline'

    retry_count = 0
    shell = None

    if dto.getTor():
        workflow_tor.renewConnection()

    try:
        while retry_count < dto.getRetries():
            if dto.getServer():
                server_history.addHistory(dto, infos[0], infos[1], platform, "Running",  infos[2])


            if dto.getDownloadLegacy():
                dto.publishLoggerInfo("You are using the Legacy downloader")
                result = os.system('echo \'' + command + '\' >&1 | bash')
            else:
                # run command in a "sub"-Shell, so we can monitor the output/exit
                shell = ShellManager()
                shell.send_command(command)

                # Wait and print output until the command finishes, errors out, or needs to be restarted
                result = shell.wait_for_command(timeout=30)
                
                # Ensure shell is stopped in all cases
                shell.stop()
                
                if result == 'timeout':
                    # No output for 30 seconds, increment retry counter and restart
                    retry_count += 1
                    shell.stop()
                    dto.publishLoggerWarn(f"Retrying {retry_count}/{dto.getRetries()} due to timeout...")
                elif result != 0:
                    # Command finished with an error
                    retry_count += 1
                    shell.stop()
                    dto.publishLoggerWarn(f"Retrying {retry_count}/{dto.getRetries()} due to error with exit code {result}...")


            # Check the final status
            if retry_count >= dto.getRetries():
                dto.publishLoggerWarn("Command failed after maximum retries.")
            else:
                if result == 0:
                    dto.publishLoggerInfo("Command executed successfully.")
                else:
                    dto.publishLoggerError(f"Command failed with exit code {result}.")


            if result is None or int(result) > 0:
                if result == 2048:
                    return result
                else:
                    dto.publishLoggerError('Error Code: ' + str(result))
                    retry_count += 1

                    if dto.getServer():
                        server_history.addHistory(dto, infos[0], infos[1], platform, "Pending",  infos[2])

                    timer = random.randint(200,1000)/100
                    dto.publishLoggerInfo('sleep for ' + str(timer) + 's')
                    time.sleep(timer)

                    if retry_count == dto.getRetries():
                        if dto.getServer():
                            server_history.addHistory(dto, infos[0], infos[1], platform, "Failed",  infos[2])

                        dto.publishLoggerWarn('the Command was: %s' % command)
                        dto.publishLoggerError(platform + ' - error at downloading: ' + content)

                        return result

            else:
                if dto.getServer():
                    server_history.addHistory(dto, infos[0], infos[1], platform, "Finished",  infos[2])

                return result


    except KeyboardInterrupt:
        if shell:
            shell.stop()  # Ensure the shell process is stopped
        dto.publishLoggerDebug('Interrupted by User')
        dto.publishLoggerError('Platform: ' + platform + ' | Content: ' + content)
        raise

    except Exception as e:
        if shell:
            shell.stop()  # Ensure the shell process is stopped
        dto.publishLoggerError(platform + ' - error at downloading: ' + str(e))
        raise  # Re-raise the exception to ensure it propagates if needed

    finally:
        # Ensure the shell process is stopped if not already stopped
        if shell:
            shell.stop()
