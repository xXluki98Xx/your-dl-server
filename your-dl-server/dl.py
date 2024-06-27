#!/usr/bin/env python3

import os
import sys
import random

import click

import your_dl_server.functions as functions
import your_dl_server.downloader as downloader
import your_dl_server.ioutils as ioutils
import your_dl_server.workflow_animescrapper as workflow_animescrapper
import your_dl_server.workflow_aria2c as workflow_aria2c
import your_dl_server.workflow_server as workflow_server
import your_dl_server.workflow_watcher as workflow_watcher
import your_dl_server.workflow_wget as workflow_wget
import your_dl_server.workflow_ydl as workflow_ydl
from your_dl_server.dto import dto


# - - - - - # - - - - - # main
@click.group()

# switch
@click.option('-v', '--verbose', default=False, is_flag=True, help='Verbose mode')
@click.option('--axel', default=False, is_flag=True, help='Using Axel as Accelerator')
@click.option('-a', '--aria2c', default=False, is_flag=True, help='Using Aria2c as Accelerator')
@click.option('-cr', '--credentials', default=False, is_flag=True, help='Need Credentials')
@click.option('-nr', '--no-remove', default=False, is_flag=True, help='remove Files at wget')
@click.option('-p', '--playlist', default=False, is_flag=True, help='Playlist')
@click.option('-s', '--single', default=False, is_flag=True, help='close after finish')
@click.option('-sc', '--skip-checks', default=False, is_flag=True, help='skip checks')
@click.option('-sy', '--sync', default=False, is_flag=True, help='')
@click.option('-ul', '--use-legacy', default=True, is_flag=True, help='')

# int
@click.option('-bw','--bandwidth', default='0B', help='Enter an Bandwidthlimit like 1.5M')
@click.option('--max-sleep', default=15, help='Enter an Number for max-Sleep between retries/ downloads')
@click.option('--min-sleep', default=2, help='Enter an Number for min-Sleep between retries/ downloads')
@click.option('-r', '--retries', default=3, help='Enter an Number for Retries')
@click.option('--connections', default=5, help='Enter an Number for Concurrent Connections')

# string
@click.option('-cf','--cookie-file', default='', help='Enter Path to cookie File')
@click.option('-d', '--debug', default='', help='Using Logging mode')
@click.option('-dl','--dub-lang', default='', help='Enter language Code (de / en)')
@click.option('-sl','--sub-lang', default='', help='Enter language Code (de / en)')

def main(retries, min_sleep, max_sleep, bandwidth, axel, cookie_file, sub_lang, dub_lang, playlist, no_remove, debug, sync, verbose, single, credentials, skip_checks, use_legacy, aria2c, connections):

    global dto
    dto = dto()
    dto.setLogger(debug)
    dto.setVerbose(verbose)
    dto.setDownloadLegacy(use_legacy)

    dto.setAxel(axel)
    dto.setAria2c(aria2c)
    # dto.setCredentials(credentials)
    dto.setPlaylist(playlist)
    dto.setRemoveFiles(no_remove)
    dto.setSingle(single)
    dto.setSkipChecks(skip_checks)
    dto.setSync(sync)

    dto.setBandwidth(bandwidth)

    dto.setCookieFile(cookie_file)
    dto.setDubLang(dub_lang)
    dto.setSubLang(sub_lang)
    dto.setRetries(retries)
    dto.setConnections(connections)

    dto.setPathToRoot(ioutils.getRootPath(dto))

    dto.setData(ioutils.loadConfig(dto.getPathToRoot()))

    parameters = '--retries {retries} --min-sleep-interval {min_sleep} --max-sleep-interval {max_sleep} --continue'.format(retries = retries, min_sleep = min_sleep, max_sleep = max_sleep)
    dto.setParameters(parameters)


# - - - - - # - - - - - # rename command
@main.command(help='Path for rename, not file')

# string
@click.option('-os', '--offset', default=0, help='String Offset')
@click.option('-c', '--cut', default=0, help='Cut String')
@click.option('-o', '--old', default='', help='old String')
@click.option('-n', '--new', default='', help='new String')

# arguments
@click.argument('rename', nargs=-1)

def rename(rename, offset, cut, old, new):

    for itemPath in rename:
        functions.func_rename(dto, itemPath, offset, cut, old, new)


# - - - - - # - - - - - # convertFiles command
@main.command(help='ffmpeg File convert')

# switch
@click.option('-nf', '--no-fix', default=False, is_flag=True, help='fixing')
@click.option('-nr', '--no-renaming', default=False, is_flag=True, help='Directories Rename?')

# string
@click.option('-sp', '--subpath', default='', help='Path which will contain the new Files')
@click.option('-vc', '--vcodec', default='', help='new Video Codec')
@click.option('-ac', '--acodec', default='copy', help='new Audio Codec')

# arguments
@click.argument('newformat', nargs=1)
@click.argument('path', nargs=-1)

def convertFiles(newformat, path, subpath, vcodec, acodec, no_fix, no_renaming):

    try:
        for itemPath in path:
            itemPathComplete = os.path.join(os.getcwd(), itemPath)

            dto.publishLoggerDebug('convertFiles')
            dto.publishLoggerDebug('filePathComplete: ' + itemPath)

            if os.path.isfile(itemPathComplete):
                dto.publishLoggerDebug('is File: ' + str(os.path.isfile(itemPathComplete)))
                functions.func_convertFilesFfmpeg(dto, itemPathComplete, newformat, subpath, vcodec, acodec, no_fix)


            if os.path.isdir(itemPathComplete):
                dto.publishLoggerDebug('is Dir: ' + str(os.path.isdir(itemPathComplete)))
                functions.func_convertDirFiles(dto, itemPathComplete, newformat, subpath, vcodec, acodec, no_fix)

                if not no_renaming:
                    try:
                        os.rename(itemPath, ioutils.formatingDirectories(itemPath))
                    except:
                        pass


    except:
        dto.publishLoggerError('convertfiles - error at ffmpeg: ' + str(sys.exc_info()))

    ioutils.elapsedTime(dto)


# - - - - - # - - - - - #
@main.command(help='ffmpeg file merge')

# arguments
@click.argument('newformat', nargs=1)
@click.argument('paths', nargs=-1)

def mergeFiles(paths, newformat):

    for path in paths:
        functions.func_ffmpegDirMerge(dto, path, newformat)


# - - - - - # - - - - - # divideAndConquer command
@main.command(help='divide and conquer for large list')

# switch
@click.option('-r', '--reverse', default=False, is_flag=True, help='reverse')

# string
@click.option('-d', '--dir', default='', help='Path which will contain the new Files')
@click.option('-f', '--file', default='', help='Path which will contain the new Files')

# int
@click.option('-cs', '--chunck-size', default=10, help='Enter an Number for Chunksize')

# arguments
@click.argument('url', nargs=1)

def dnc(url, file, dir, chunck_size, reverse):
    if os.path.isfile(url):
        file = url

    if not os.path.isfile(file):
        ioutils.getLinkList(dto, url, file)

    dto.publishLoggerDebug('dnc')

    urlList = ioutils.openfile(dto, file)
    urlCopy = urlList.copy()

    chunkedList = list(ioutils.chunks(dto, urlCopy, chunck_size))

    if reverse:
        chunkedList.reverse()

    for itemList in chunkedList:

        random.shuffle(itemList)

        try:
            dto.publishLoggerDebug('downloading: ' + str(itemList))

            # if dl == 'wget':
            #     if download_wget2(str(item), dir) == 0:
            #         urlCopy.remove(item)
            #         print('\nremoved: ' + str(item) + ' | rest list ' + str(urlCopy))

            # if dl == 'aria':
            if downloader.download_aria2c_dnc(dto, itemList, dir) == 0:
                for i in itemList:
                    urlCopy.remove(i)

                dto.publishLoggerDebug('removed: ' + str(itemList) + ' | rest list ' + str(urlCopy))

        except KeyboardInterrupt:
            ioutils.savefile(dto, file, urlCopy, "aria2c-dnc")

            dto.publishLoggerWarn('Interupt by User')
            ioutils.elapsedTime(dto)
            os._exit(1)
            break

        except:
            dto.publishLoggerError('divideAndConquer - error at list: ' + str(sys.exc_info()))

        finally:
            # will always be executed last, with or without exception
            ioutils.savefile(dto, file, urlCopy, "aria2c-dnc")

    ioutils.elapsedTime(dto)


# - - - - - # - - - - - # wget
@main.command(help='wget downloader')

# switch
@click.option('-sp', '--space', default=False, is_flag=True, help='check if old file are deletable')

# string
@click.option('-p', '--params', default='', help='String of params')

# arguments
@click.argument('wget', nargs=-1)
def wget(wget, space, params):

    if wget != '':
        dto.publishLoggerDebug('wget')

        dto.setSpace(space)

        workflow_wget.wget(dto, wget, params)
    else:
        dto.publishLoggerError('wget - no items')


# - - - - - # - - - - - # youtube-dl
@main.command(help='YoutubeDL downloader usage: dl.py [options] ydl url;tile;referer;directory')

#String
@click.option('-os', '--offset', default=0, help='String Offset')

# arguments
@click.argument('url', nargs=-1)
def ydl(url, offset):

    if url != '':
        dto.publishLoggerDebug('youtube-dl')

        dto.setOffset(offset)

        workflow_ydl.ydl(dto, url)
    else:
        dto.publishLoggerError('ydl - no url')


# - - - - - # - - - - - # aria2c
@main.command(help='Aria2c downloader')

# arguments
@click.argument('url', nargs=-1)
def aria2c(url):

    if url != '':
        dto.publishLoggerDebug('aria2c')

        workflow_aria2c.aria2c(dto, url)
    else:
        dto.publishLoggerError('aria2c - no url')


# - - - - - # - - - - - # Anime
@main.command(help='Animescrapper')

#String
@click.option('-g', '--group', default='er', help='Sub Group')
@click.option('-s', '--show', default='', help='Anime Show')
@click.option('-q', '--quality', default='1080', help='Video Quality')
@click.option('-a', '--start', default='1', help='first Episode')
@click.option('-z', '--end', default='12', help='last Episode')
@click.option('-d', '--dir', default='', help='Path to be downloaded')

#Switch
@click.option('-f', '--file', default=False, is_flag=True, help='download .torrent files')

def anime(group, show, quality, start, end, file, dir):

    if show != '':
        workflow_animescrapper.anime(dto, group, show, quality, start, end, file, dir)
    else:
        dto.publishLoggerError('anime - no show')


# - - - - - # - - - - - # Watcher
@main.command(help='Enter an dl.py Command (String) to be run as Watcher, Time is used as time between.')

#String
@click.option('-m', '--minutes', default='5', help='minutes')
@click.option('-h', '--hours', default='0', help='hours')

#Switch
# @click.option('-f', '--file', default=False, is_flag=True, help='download .torrent files')

@click.argument('watcher', nargs=1)
def watcher(watcher, minutes, hours):

    if watcher != '':
        workflow_watcher.watcher(dto, watcher, minutes, hours)
    else:
        dto.publishLoggerError('watcher - no command')


# - - - - - # - - - - - # Server
@main.command(help='Webgui for dl Utility')

# String
@click.option('-h', '--host', default='0.0.0.0', help='Host')
@click.option('-p', '--port', default='8080', help='Port')
@click.option('-d', '--dir', default='ydl-downloads', help='Path which will contain the new Files')
# @click.option('-sp', '--subpath', default='downloads', help='Path which will contain the new Files')

# Int
@click.option('-w', '--worker', default=8, help='Port')

# Switch
@click.option('--local', default=False, is_flag=True, help='local')
@click.option('--hidden', default=False, is_flag=True, help='displaying hidden files')

def server(host, port, worker, dir, local, hidden):

    dto.setServer(True)
    server = workflow_server.Server(host, port, worker, dir, local, hidden)
    server.setup()
    server.start()


# - - - - - # - - - - - # Disk
@main.command(help='Create an Compressed Backup from Disk')

# String
@click.option('-s', '--source', default='', help='Source')
@click.option('-t', '--target', default='', help='Target')
@click.option('-p', '--path', default='./', help='Subpath which will contain the new Files')

# Switch
@click.option('--not-backup', default=False, is_flag=True, help='Backup or Restore (default Backup)')
@click.option('--not-compress', default=False, is_flag=True, help='Compressed or Raw (default Compressed)')

def disk(source, target, path, not_backup, not_compress):

    if source != '' and target != '':
        if not not_backup:
            if not not_compress:
                os.system('sudo dd if=' + source + ' conv=sync,noerror bs=64K status=progress | gzip -c  > ' + path + target + '.img.gz')
            else:
                os.system('sudo dd if=' + source + ' of=' + path + target + '.img conv=sync,noerror bs=64K status=progress ')
        else:
            if not not_compress:
                os.system('gunzip -c ' + source  + ' | dd of=' + target + ' conv=sync,noerror bs=64K')
            else:
                os.system('sudo dd if=' + source + ' of=' + target + ' conv=fdatasync status=progress')

    else:
        dto.publishLoggerError('disk - missing param')

    ioutils.elapsedTime(dto)


# - - - - - # - - - - - # Disk
@main.command(help='Update git repo and packages')

# Switch
@click.option('-p', '--pip', default=False, is_flag=True, help='update pip Packages?')

def update(pip):

    ioutils.update(dto, pip)

    ioutils.elapsedTime(dto)


# ----- # ----- # livedisk
@main.command(help="Enter an List with URL for LiveDisk Sync")
@click.argument("listFiles", nargs= -1)
def livedisk(listFiles):

    dto.setSync(True)

    for listFile in listFiles:

        if listFile != '':
            dto.publishLoggerDebug('liveDisk')

            downloader.download_wget(dto, listFile, '--no-http-keep-alive -A "*.iso" -A "*.raw.xz"')
        else:
            dto.publishLoggerError('liveDisk - no url')


# ----- # ----- #
@main.command(help="Enter an Filename and a Root Path for ydl download")
@click.argument("filenames", nargs= -1)

@click.option('-d', '--directory', default='.', help='Root Path for file search')

def filewalker(filenames, directory):

    origPath = os.getcwd()

    dto.publishLoggerDebug('filewalker')

    for filename in filenames:
        filePaths = ioutils.findFiles(filename, directory)

        dto.publishLoggerDebug('filewalker - founds - {}'.format(filePaths))

        for filePath in filePaths:
            dto.publishLoggerDebug('filewalker - current download - {}'.format(filePath))

            workDir = filePath[:-len(filename)]
            os.chdir(workDir)
            dto.publishLoggerDebug('filewalker - change Dir - {}'.format(workDir))

            workflow_ydl.ydl_list(dto, filePath)

            os.chdir(origPath)


# - - - - - # - - - - - # main
if __name__ == '__main__':
    main()
    pass
