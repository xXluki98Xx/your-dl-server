import json
import os
import re
import subprocess
import sys
from datetime import datetime

import bs4
import requests
import safer

from dto import dto


# ----- # ----- #
def constructPath(path):
    '''
    Needed for File Serving
    Convert path to windows path format.
    '''
    if(sys.platform=='win32'):
      return "\\"+path.replace('/','\\')
    return path #Return same path if on linux or unix


def getRootPath(dto):
    pathToRoot = ''

    # for server mode
    if os.path.isdir('/app/your-dl-server/'):
        pathToRoot = '/app/your-dl-server/your-dl-server'        

    else:
        try:
            path = os.getenv('PATH').split(':')

            names = ['dl', 'dl.py']

            for name in names:
                for subPath in path:
                    if os.path.isfile(os.path.join(subPath, name)) != '':
                        pathToRoot = subPath
                        break

                pathToRoot = pathToRoot.replace(name,'').rstrip('\n')
        except:
            pathToRoot = os.getcwd()


    dto.publishLoggerDebug('rootpath is: ' + pathToRoot)
    return pathToRoot


def update(dto):
    path = os.path.dirname(dto.getPathToRoot())
    updateRepo(dto, path)
    updatePackages(dto, path)


def updateRepo(dto, path):
    dto.publishLoggerInfo('Sync Git Repo')

    proc = subprocess.Popen(
        ['git', 'pull'], cwd=path, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )

    output, error = proc.communicate()

    dto.publishLoggerDebug(output.decode('ascii'))
    dto.publishLoggerError(error.decode('ascii'))


def updatePackages(dto, path):
    dto.publishLoggerInfo('Updating Packages')

    path = os.path.join(path, 'requirements.txt')
    command = ['pip3', 'install', '-U', '-r', path]

    proc = subprocess.Popen(
        command, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )

    output, error = proc.communicate()

    dto.publishLoggerDebug(output.decode('ascii'))
    dto.publishLoggerError(error.decode('ascii'))


def loadConfig(pathToRoot):
    path = os.path.join(pathToRoot, 'env')

    with open(path) as json_file:
        data = json.load(json_file)

    return data


def getMainParametersFromDto(dto):
    parameters = ''

    # switches
    if dto.getVerbose():
        parameters += ' --verbose'

    if dto.getAxel():
        parameters += ' --axel'

    if dto.getCredentials():
        parameters += ' --credentials'

    if dto.getPlaylist():
        parameters += ' --playlist'

    if dto.getRemoveFiles():
        parameters += ' --no-remove'

    if dto.getSingle():
        parameters += ' --single'

    if dto.getSkipChecks():
        parameters += ' --skip-checks'

    if dto.getSync():
        parameters += ' --sync'

    
    # int
    if dto.getBandwidth():
        parameters += ' --bandwidth ' + dto.getBandwidth()


    # string
    if dto.getCookieFile() != '':
        parameters += ' --cookie-file ' + dto.getCookieFile()

    if dto.getLogging() != '':
        parameters += ' --debug ' + dto.getLogging()

    if dto.getDubLang() != '':
        parameters += ' --dub-lang ' + dto.getDubLang()

    if dto.getSubLang() != '':
        parameters += ' --sub-lang ' + dto.getSubLang()

    return parameters


# ----- # ----- #
def testWebpage(dto, url):
    if not dto.getSkipChecks():
        dto.publishLoggerDebug('webpage test for: ' + url)

        req = requests.get(url, headers = {'User-Agent': 'Mozilla/5.0'})

        if req.status_code > 300:
            dto.publishLoggerDebug('HTTP Error: ' + str(req.status_code))
            return req.status_code

    return 0


# ----- # ----- # help
def getTitleFormated(title):
    newTitle = ''

    if title == '':
        now = datetime.now()
        newTitle = 'dl_' + now.strftime('%m-%d-%Y_%H-%M-%S')
        return newTitle
    else:
        newTitle = title

    newTitle = formatingFilename(newTitle)

    while newTitle.endswith('-'):
        newTitle = newTitle[:-1]

    while newTitle.startswith('-'):
        newTitle = newTitle[1:]

    return newTitle


def bytes2human(n):
    symbols = ('K', 'M', 'G', 'T', 'P', 'E', 'Z', 'Y')
    prefix = {}
    for i, s in enumerate(symbols):
        prefix[s] = 1 << (i+1)*10
    for s in reversed(symbols):
        if n >= prefix[s]:
            value = float(n) / prefix[s]
            return '%.1f%s' % (value, s)

    return '%sB' % n


def human2bytes(n):
    size = n[-1]

    switcher = {
        'B': 1,
        'K': 1000,
        'M': pow(1000,2),
        'G': pow(1000,3),
    }

    swapSize = float(n[:-1]) * switcher.get(size, 0)

    return '%s' % int(swapSize)


def getAccelerator(dto):
    parameters = ''
    extParams = ''

    if dto.getAxel():
        parameters += ' --external-downloader axel'
        extParams = '-s {}'.format(human2bytes(dto.getBandwidth()))

    if dto.getAria2c():
        parameters += ' --external-downloader aria2c'
        extParams = '-x 8 -j 16 --continue --min-split-size=1M --optimize-concurrent-downloads --max-overall-download-limit {}'.format(human2bytes(dto.getBandwidth()))

    if parameters != '':
        parameters += ' --external-downloader-args "{}"'.format(extParams)

    return parameters


def getBandwith(dto, plattform):
    parameters = ''

    if dto.getBandwidth() == '0B':
        return ''

    if plattform == 'wget' or plattform == 'ydl':
        parameters += ' --limit-rate'

    if plattform == 'aria2c':
        parameters += ' --max-overall-download-limit'

    return parameters + ' {}'.format(human2bytes(dto.getBandwidth()))


# ----- # ----- # formating
def formatingDirectories(text):
    if text.startswith('.'):
        return

    reg = re.compile(r'[^\w\d\s\-\_\/\.\|]')
    reg3 = re.compile(r'-{3,}')

    swap = text.casefold()
    swap = re.sub(reg, '', swap)
    swap = swap.replace(' ', '-').replace('_','-').replace('+','-').replace('|', '-')

    swap = re.sub(reg3, '§', swap)
    swap = swap.replace('--', '-')
    swap = swap.replace('§', '---')

    return swap


def formatingFilename(text):
    regCharacters = re.compile(r'[^\w\d\s\-\_\/\.+|]')
    regBrackets = re.compile(r'\[(.*?)\]')
    reg3 = re.compile(r'-{3,}')

    extensionsList = [
                        '.mp4', '.mkv', '.avi', '.m4a', '.mov',
                        '.flac', '.wav', '.mp3', '.aac',
                        '.py', '.txt', '.md', '.pdf', '.doc', 'docx',
                        '.iso', '.zip', '.rar',
                        '.jpg', '.jpeg', '.svg', '.png',
                        '.csv', '.html', '.ppt', '.pptx', '.xls', '.xlsx',
                        '.log',
                    ]

    swap = text.casefold()

    swap = re.sub(regBrackets, '', swap)
    swap = re.sub(regCharacters, '', swap)

    if any(ext in swap for ext in extensionsList):
        fileSwap = swap.rsplit('.',1)
        swap = fileSwap[0].replace('/','').replace('.','') + '.' + fileSwap[1]
    else:
        swap = swap.replace('/','').replace('.','')

    swap = swap.replace(' ', '-').replace('_','-').replace('+','-').replace('|','-')

    swap = re.sub(reg3, '§', swap)
    swap = swap.replace('--', '-')
    swap = swap.replace('§', '---')

    if any(ext in swap for ext in extensionsList):
        fileSwap = swap.rsplit('.',1)
        swap = getTitleFormated(fileSwap[0]) + '.' + fileSwap[1]

    return swap


# ----- # ----- # time measurement
def elapsedTime(dto):
    time_elapsed = datetime.now() - dto.getTimeStart()
    dto.publishLoggerInfo('Time elapsed (hh:mm:ss.ms): {}'.format(time_elapsed))


# ----- # ----- # divide and conquer
def getLinkList(link, listFile):
    dto.publishLoggerInfo('beginning link extraction')

    page = requests.get(link)
    if page.status_code == 200:
        dto.publishLoggerInfo('got page')
        content = page.content

        DOMdocument = bs4.BeautifulSoup(content, 'html.parser')

        listLinks = []

        # for a in DOMdocument.find_all('a'):
        #     if 'serie/' in a:
        #         listLinks.append(a.string)

        dto.publishLoggerInfo('writting links to file')
        with safer.open(listFile, 'w') as f:
            for url in listLinks:
                if 'pdf' in url:
                    f.write(link+'%s\n' % url)
        dto.publishLoggerInfo('finished writing')


def split_list(alist, wanted_parts=1):
    length = len(alist)
    return [ alist[i*length // wanted_parts: (i+1)*length // wanted_parts]
        for i in range(wanted_parts) ]


def chunks(lst, n):
    '''Yield successive n-sized chunks from lst.'''
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


def openfile(dto, filename):
    dto.publishLoggerInfo('reading from file: ' + filename)

    try:
        with open(filename, 'r') as f:
            data = f.readlines()
            data = [x.strip() for x in data]
    except:
        data = []

    return data


def savefile(dto, filename, data, kind):
    dto.publishLoggerInfo('writing to file: ' + filename)
    
    try:
        with open(filename, 'w') as f:

            if kind == 'history':
                f.writelines("# History Log: " + datetime.now().strftime("%Y-%m-%d_%H-%M-%S\n"))

                for item in data:
                    dto.publishLoggerDebug("saveHistory: item\n" + str(item))
                    f.writelines("{url};{title};{kind};{status};{path};{timestamp};\n".format(url=item['url'], title=item['title'], kind=item['kind'],status=item['status'], path=item['path'], timestamp=item['timestamp']))

                return

            for item in data:
                f.write('%s\n' % item)

    except:
        dto.publishLoggerError('error at writing data to file: ' + str(sys.exc_info()))