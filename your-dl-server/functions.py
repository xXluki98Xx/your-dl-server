import grp
import os
import pwd
import shutil
import stat
import sys
from datetime import datetime
from pathlib import Path

import ffmpeg

import ioutils


def func_renameEpisode(season, episode, title, seasonOffset):
    f = 's'
    if len(season) == 1:
        f += '0' + str( int(season) + int(seasonOffset))
    else:
        f += str( int(season) + int(seasonOffset))

    f += 'e'
    if len(episode) == 1:
        f += '0' + episode
    else:
        f += episode
    f += '-' + title

    return f


# ----- # ----- # file operations
def func_rename(dto, filePath, offset, cut):
    if os.path.isfile(filePath):
        path, origFile = os.path.split(filePath)

        if origFile.startswith('.'):
            return

        file = ioutils.formatingFilename(origFile)

        if offset > 0:
            file = file[offset:]
        if cut > 0:
            file = file[:-cut]

        old = os.path.join(path, origFile)
        new = os.path.join(path, file)

        dto.publishLoggerDebug('function - func_rename: rename file from {} to {}'.format(old, new))
        os.rename(old, new)


    if os.path.isdir(filePath):
        try:
            path, dirs, files = next(os.walk(filePath))

            for directory in dirs:
                if directory.startswith('.'):
                    continue
                func_rename(dto, os.path.join(filePath, directory), offset, cut)

            for file in files:
                func_rename(dto, os.path.join(filePath, file), offset, cut)


        except:
            dto.publishLoggerError('function - func_rename: ' + str(sys.exc_info()))
            dto.publishLoggerWarn('function - func_rename: could the path be wrong?')

        try:
            path, origDir = os.path.split(filePath)
            new = os.path.join(path, ioutils.formatingDirectories(origDir))

            dto.publishLoggerDebug('function - func_rename: rename directory from {} to {}'.format(filePath, new))
            os.rename(filePath, new)
        except:
            pass


def func_replace(dto, filePath, old, new):
    try:
        path, dirs, files = next(os.walk(filePath))

        for directory in dirs:
            func_replace(dto, os.path.join(filePath, directory), old, new)

        for f in os.listdir(path):
            oldFile = os.path.join(path,f)
            f = f.replace(old, new)
            newFile = os.path.join(path, ioutils.formatingFilename(f))
            os.rename(oldFile, newFile)

    except:
        dto.publishLoggerError(' function - func_replace: ' + str(sys.exc_info()))
        dto.publishLoggerWarn('function - func_rename: could the path be wrong?')


    try:
        os.rename(filePath, ioutils.formatingDirectories(filePath))
    except:
        pass


def func_removeFiles(dto, path, file_count_prev):
    if not dto.getRemoveFiles():
        dto.publishLoggerInfo('Removing old files')

        # file count
        path, dirs, files = next(os.walk(path))
        file_count = len(files)

        dto.publishLoggerDebug('files before: ' + str(file_count_prev))
        dto.publishLoggerDebug('files after: ' + str(file_count))

        if (file_count > file_count_prev):
            files = []
            index = 0
            for f in os.listdir(path):
                index += 1
                if ( os.stat(os.path.join(path,f)).st_mtime < (datetime.now().timestamp() - (6 * 30 * 86400)) ):
                    files.append(os.path.join(path,f))

            if index > len(files):
                for i in files:
                    dto.publishLoggerDebug('removing: ' + i)
                    os.remove(os.path.join(path, i))

        else:
            files = []
            index = 0
            for f in os.listdir(path):
                index += 1
                if ( os.stat(os.path.join(path,f)).st_mtime < (datetime.now().timestamp() - (12 * 30 * 86400)) ):
                    files.append(os.path.join(path,f))

            if index > len(files):
                for i in files:
                    dto.publishLoggerDebug('removing: ' + i)
                    os.remove(os.path.join(path, i))

        dto.publishLoggerDebug('finished Removing')


# ----- # ----- # convert files
def func_convertDirFiles(dto, path, newformat, subpath, vcodec, acodec, fix):
    try:
        paths, dirs, files = next(os.walk(path))

        pathList = [
            'fix', 'abort', 'swap', 'orig', subpath,
        ]

        dto.publishLoggerDebug('convertDirFiles')
        dto.publishLoggerDebug('path: ' + path)
        dto.publishLoggerDebug('dirs: ' + str(dirs))
        dto.publishLoggerDebug('file count: ' + str(len(files)))

        for f in files:
            if f.startswith('.'):
                continue

            filePath = os.path.join(path, f)

            dto.publishLoggerDebug('filePath: ' + filePath)
            dto.publishLoggerDebug('file: ' + f)

            func_convertFilesFfmpeg(dto, filePath, newformat, subpath, vcodec, acodec, fix)

        for d in dirs:
            if d.startswith('.'):
                continue

            if any(paths in d for paths in pathList):
                continue

            nextPath = os.path.join(paths, d)

            dto.publishLoggerDebug('newformat: ' + newformat)
            dto.publishLoggerDebug('nextPath: ' + nextPath)
            dto.publishLoggerDebug('ffmpeg: ' + str(ffmpeg))

            func_convertDirFiles(dto, nextPath, newformat, subpath, vcodec, acodec, fix)
    except:
        dto.publishLoggerError('function - func_convertDirFiles: ' + str(sys.exc_info()))


def func_convertFilesFfmpeg(dto, fileName, newFormat, subPath, vcodec, acodec, fix):
    prePath, fileOrig = os.path.split(fileName)

    # if file has no format
    if fileOrig.find('.') == -1:
        return
    
    fileTarget = ''
    sourceFile = prePath + fileOrig

    pathAbort = prePath + 'abort/'
    pathFix = prePath + 'fix/'
    pathSwap = prePath + 'swap/'
    pathFinish = prePath + 'orig/'

    try:
        output = ''
        newFile = fileOrig.rsplit('.', 1)[0]
        title = ioutils.getTitleFormated(newFile)

        if subPath:
            dto.publishLoggerDebug('create subPath')
            dto.publishLoggerDebug('subPath: ' + subPath)
            dto.publishLoggerDebug('newFile: ' + newFile)
            dto.publishLoggerDebug('subPath: ' + str(prePath + subPath))
            dto.publishLoggerDebug('subPath exist: ' + str(os.path.exists(prePath + subPath)))

            path = prePath + subPath

            if not os.path.exists(path):
                os.makedirs(path)

            output = subPath + '/' + title

        else:
            output = title

        fileTarget = output + '.' + newFormat

        dto.publishLoggerDebug('originalFile: ' + fileOrig)
        dto.publishLoggerDebug('output: ' + fileTarget)
        dto.publishLoggerDebug('fix: ' + str(not fix))

        if os.path.isfile(prePath + fileTarget):
            dto.publishLoggerWarn('file exist already, move original to abort folder')

            if not os.path.isdir(pathAbort):
                os.mkdir(pathAbort)

            try:
                shutil.move(prePath + fileOrig, pathAbort + fileOrig)
            except:
                pass

            return

        if not fix:
            try:
                dto.publishLoggerDebug('fixing')
                dto.publishLoggerDebug('fileOrig: ' + prePath + fileOrig)
                dto.publishLoggerDebug('fileFix: '+ pathFix + fileOrig)
                dto.publishLoggerDebug('exist?: ' + str(os.path.isfile(pathFix + fileOrig)))

                if not os.path.isdir(pathFix):
                    os.mkdir(pathFix)

                ffmpeg.input(prePath + fileOrig).output(pathFix + fileOrig, vcodec='copy', acodec='copy', map='0', **{'bsf:v': 'mpeg4_unpack_bframes'}).run()

            except KeyboardInterrupt:
                dto.publishLoggerWarn('Interupt by User')
                os._exit(1)

            except:
                dto.publishLoggerError('function - func_convertFilesFfmpeg at fixing: ' + str(sys.exc_info()))
                try:
                    os.remove(pathFix + fileOrig)
                except:
                    pass

        if os.path.isfile(pathFix + fileOrig):
            sourceFile = pathFix + fileOrig

        if vcodec != '':
            try:
                ffmpeg.input(sourceFile).output(prePath + fileTarget, vcodec=vcodec, acodec=acodec, map='0').run()

            except KeyboardInterrupt:
                dto.publishLoggerWarn('Interupt by User')
                os._exit(1)

            except:
                dto.publishLoggerError('function - func_convertFilesFfmpeg with vcodec first try: ' + str(sys.exc_info()))

                # Posible data lose
                fileSwap = newFile + '.' + newFormat

                dto.publishLoggerDebug('swapFile: ' + fileSwap)
                dto.publishLoggerDebug('fileTarget: ' + fileTarget)

                os.remove(prePath + fileTarget)

                if not os.path.isdir(pathSwap):
                    os.mkdir(pathSwap)

                try:
                    ffmpeg.input(sourceFile).output(pathSwap + fileSwap, map='0', scodec='copy').run()
                    ffmpeg.input(pathSwap + fileSwap).output(prePath + fileTarget, map='0', vcodec=vcodec, acodec=acodec, scodec='copy').run()

                except:
                    dto.publishLoggerError('function - func_convertFilesFfmpeg with vcodec second try with swapping: ' + str(sys.exc_info()))
                    dto.publishLoggerWarn('function - broken file: ' + sourceFile)

                    try:
                        dto.publishLoggerDebug('pathAbort: ' + pathAbort)
                        dto.publishLoggerDebug('fileOrig: ' + prePath+fileOrig)
                        dto.publishLoggerDebug('swapFile: ' + prePath+fileSwap)
                        dto.publishLoggerDebug('fileTarget: ' + prePath+fileTarget)

                        if not os.path.isdir(pathAbort):
                            os.mkdir(pathAbort)

                        shutil.move(prePath + fileOrig, pathAbort + fileOrig)

                        os.remove(prePath + fileSwap)
                        os.remove(prePath + fileTarget)
                    except:
                        dto.publishLoggerError('function - func_convertFilesFfmpeg with vcodec second try with swapping at swap removing: ' + str(sys.exc_info()))


        else:
            try:
                dto.publishLoggerDebug('fileTarget: ' + fileTarget)
                ffmpeg.input(sourceFile).output(prePath + fileTarget).run()

            except KeyboardInterrupt:
                dto.publishLoggerWarn('Interupt by User')
                os._exit(1)

            except:
                dto.publishLoggerError('function - func_convertFilesFfmpeg at simple converting: ' + str(sys.exc_info()))

        dto.publishLoggerDebug('Permissions: ' + oct(stat.S_IMODE(os.lstat(prePath + fileOrig).st_mode)))
        dto.publishLoggerDebug('owner: ' + Path(prePath + fileOrig).owner() + ' | ' + str(pwd.getpwnam(Path(prePath + fileOrig).owner()).pw_uid))
        dto.publishLoggerDebug('group: ' + Path(prePath + fileOrig).group() + ' | ' + str(grp.getgrnam(Path(prePath + fileOrig).group()).gr_gid))

        dto.publishLoggerDebug('changing permission on: ' + prePath+fileTarget)
        Path(prePath + fileTarget).chmod(stat.S_IMODE(os.lstat(prePath + fileOrig).st_mode))
        os.chown(prePath + fileTarget, pwd.getpwnam(Path(prePath + fileOrig).owner()).pw_uid, grp.getgrnam(Path(prePath + fileOrig).group()).gr_gid)

        try:
            dto.publishLoggerDebug('pathFinish: ' + pathFinish)
            dto.publishLoggerDebug('sourceFile: ' + sourceFile)
            dto.publishLoggerDebug('origFile: ' + prePath + fileOrig)

            if not os.path.isdir(pathFinish):
                os.mkdir(pathFinish)

            shutil.move(prePath + fileOrig, pathFinish + fileOrig)
        except:
            dto.publishLoggerError('function - func_convertFilesFfmpeg finish at orig directory')

    except KeyboardInterrupt:
        dto.publishLoggerWarn('Interupt by User')
        os._exit(1)

    except:
        dto.publishLoggerError('function - func_convertFilesFfmpeg: ' + str(sys.exc_info()))

    finally:
        if os.path.isdir(pathSwap):
            shutil.rmtree(pathSwap)

        if os.path.isdir(pathFix):
            shutil.rmtree(pathFix)
