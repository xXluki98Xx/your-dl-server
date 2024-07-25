import re

import requests
from yt_dlp import YoutubeDL

import your_dl_server.downloader as downloader
import your_dl_server.ioutils as ioutils
from your_dl_server.functions import *


# ----- # ----- #
def getLanguage(dto, platform):
    output = '--no-mark-watched --hls-prefer-ffmpeg --socket-timeout 15'

    if platform == 'crunchyroll':
        output += ' --all-subs --embed-subs --write-sub --merge-output-format mkv --recode-video mkv'
        if dto.getDubLang() == 'de': return output + ' --format "best[format_id!*=hardsub][format_id*=adaptive_hls-audio-deDE]"'

        return output + ' --format "best[format_id!*=hardsub][format_id*=adaptive_hls-audio-jaJP]"'

    # if platform == 'animeondemand':
    #     output += ' --all-subs --embed-subs --write-sub --merge-output-format mkv --recode-video mkv'
    #     if dto.getDubLang() == 'de': return output + ' --format "best[format_id*=ger-Dub]"'

    #     return output + ' --format "best[format_id*=ger-Dub]"'

    return output

def getUserCredentials(dto, platform):
    parameter = ''

    if dto.getCookieFile():
        parameter += ' --cookies ' + dto.getCookieFile()
    else:
        if platform in dto.getData():
            parameter += ' --username ' + dto.getData()[platform].get('username') + ' --password ' + dto.getData()[platform].get('password') + ' '


    dto.publishLoggerDebug(parameter)

    return parameter


# ----- # ----- #
def ydl_extractor(dto, content):
    title = ''
    stringReferer = ''
    directory = '.'

    if ('magnet:?xt=urn:btih' in content):
        try:
            (url, directory) = content.split(';')
        except ValueError:
            url = content
            directory = ''

        dto.publishLoggerInfo('current Download: ' + url)
        return downloader.download_aria2_magnet(dto, url, directory)

    try:
        (url, title, stringReferer, directory) = content.split(';')
    except ValueError:
        try:
            (url, title, stringReferer) = content.split(';')
        except ValueError:
            try:
                (url, title) = content.split(';')
            except ValueError:
                url = content

    webpageResult = ioutils.testWebpage(dto, url.split('?')[0])
    if webpageResult != 0:
        return webpageResult

    mostly = ['fruithosted', 'oloadcdn', 'verystream', 'vidoza', 'vivo']

    dto.publishLoggerInfo('current Download: ' + url)

    for domain in mostly:
        if domain in url : return host_mostly(dto, url, title, stringReferer, directory)

    # if ('animeholics' in url) : return host_animeholics(dto, url, title, stringReferer, directory)

    if ('haho.moe' in url):
        if (url[-1] == '/'):
            url = url[:-1]

        if (len(url.rsplit('/',1)[1]) < 3):
            return host_hahomoe(dto, url, title, stringReferer, directory)
        else:
            i = 1
            while ioutils.testWebpage(dto, url+'/'+str(i)) == 0:
                ydl_extractor(dto, url+'/'+str(i))
                i += 1

            i = 1
            while ioutils.testWebpage(dto, url+'/s'+str(i)) == 0:
                ydl_extractor(dto, url+'/s'+str(i))
                i += 1

            return 0


    if ('sxyprn' in url) : return host_sxyprn(dto, url, title, stringReferer, directory)
    if ('porngo' in url) : return host_porngo(dto, url, title, stringReferer, directory)
    if ('xvideos' in url) : return host_xvideos(dto, url, title, stringReferer, directory)

    if ('udemy' in url) : return host_udemy(dto, url, title, stringReferer, directory)
    if ('vimeo' in url) : return host_vimeo(dto, url, title, stringReferer, directory)
    if ('cloudfront' in url) : return host_cloudfront(dto, url, title, stringReferer, directory)
    if ('pluralsight' in url) : return host_pluralsight(dto, url, title, stringReferer, directory)

    if ('crunchyroll' in url) :
        if dto.getSync():
            return host_crunchyroll_sync(dto, url, title, stringReferer, directory)
        else:
            return host_crunchyroll(dto, url, title, stringReferer, directory)

    if ('anime-on-demand' in url) : return host_animeondemand(dto, url, title, stringReferer, directory)

    return host_default(dto, url, title, stringReferer, directory)


def host_default(dto, content, title, stringReferer, directory):
    if not dto.getPlaylist():

        ydl_opts = {
            'outtmpl': '%(title)s',
            'restrictfilenames': True,
            'forcefilename':True
        }

        try:
            if title == '':
                with YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(content, download = False)
                    filename = ydl.prepare_filename(info)

                    dto.publishLoggerDebug('extracted filename: ' + filename)

                filename = ioutils.getTitleFormated(filename)

                output = '--no-playlist --output "{dir}/{title}.%(ext)s"'.format(title = filename, dir = directory)
                return downloader.download_ydl(dto, content, dto.getParameters(), output, stringReferer, [content, filename, directory])
            else:
                filename = ioutils.getTitleFormated(title)

                output = '--no-playlist --output "{dir}/{title}.%(ext)s"'.format(title = filename, dir = directory)
                return downloader.download_ydl(dto, content, dto.getParameters(), output, stringReferer, [content, filename, directory])

        except:
            output = '--format best --no-playlist --output "{dir}/%(title)s.%(ext)s"'.format(dir = directory)
            return downloader.download_ydl(dto, content, dto.getParameters(), output, stringReferer, [content, title, directory])

    else:
        output = '--ignore-errors --format best --output "{dir}/%(extractor)s--%(playlist_uploader)s_%(playlist_title)s/%(playlist_index)s_%(title)s.%(ext)s"'.format(dir = directory)
        return downloader.download_ydl(dto, content, dto.getParameters(), output, stringReferer, [content, title, directory])


def host_mostly(dto, content, title, stringReferer, directory):
    if title == '':
        title = str(input('\nPlease enter the Title:\n'))

    title = ioutils.getTitleFormated(title)
    output = '--format best --output "{dir}/{title}.%(ext)s"'.format(title = title, dir = directory)

    return downloader.download_ydl(dto, content, dto.getParameters(), output, stringReferer, [content, title, directory])


def host_hanime(dto, content, title, stringReferer, directory):
    if title == '':
        title = content.rsplit('?',1)[0].rsplit('/',1)[1]

    title = ioutils.getTitleFormated(title)
    output = '--format best --output "{dir}/{title}.%(ext)s"'.format(title = title, dir = directory)

    return downloader.download_ydl(dto, content, dto.getParameters(), output, stringReferer, [content, title, directory])


def host_hahomoe(dto, content, title, stringReferer, directory):
    url = content
    webpage = ''

    res = requests.get(url, allow_redirects=False)
    url2 = re.findall('<iframe src="(https:\/\/haho\.moe\/embed\?v=.+)"', res.text)[0]

    if title == '':
        title = re.findall('<title>(.+)</title>',res.text)[0]

        if title:
            title = title.rsplit(' ',4)[0]
        else:
            title = ''

        title = ioutils.getTitleFormated(title)
        dto.publishLoggerDebug(title)

    res2 = requests.get(url2, allow_redirects=False, cookies=res.cookies)

    url = re.findall('<source src="(.+)" title="[0-9]{3}p" type="video/mp4">', res2.text)[0]

    output = '--format best --output "{dir}/{title}.mp4"'.format(title = title, dir = directory)

    return downloader.download_ydl(dto, url, dto.getParameters(), output, stringReferer, [content, title, directory])


def host_sxyprn(dto, content, title, stringReferer, directory):
    url = content
    stringReferer = content
    webpage = ''

    req = requests.get(url, allow_redirects=False)
    webpage = req.text

    if title == '':
        title = str(webpage).split('<title>')[1].split('</title>')[0]
        title = title.rsplit('-', 1)[0]
        title = title.casefold().replace(' ', '-').replace('.','').rsplit('-', 1)[0]

        if '#' in title:
            title = title.split('-#',1)[0]

    title = ioutils.getTitleFormated(title)

    url = re.findall("<span style='display:none' class='vidsnfo' data-vnfo='{(.*):(.+)}'><\/span>", webpage)[0][1]
    url = url.replace('"', '').replace('\\', '').split('/')
    url[1] = 'cdn8'

    content = 'https://sxyprn.com' + '/'.join(url)
    output = '--format best --output "{dir}/{title}.mp4"'.format(title = title, dir = directory)

    return downloader.download_ydl(dto, content, dto.getParameters(), output, stringReferer, [content, title, directory])


def host_xvideos(dto, content, title, stringReferer, directory):
    if title == '':
        title = content.rsplit('/',1)[1]

    title = ioutils.getTitleFormated(title)
    output = '--format best --output "{dir}/{title}.mp4"'.format(title = title, dir = directory)

    return downloader.download_ydl(dto, content, dto.getParameters(), output, stringReferer, [content, title, directory])


def host_porngo(dto, content, title, stringReferer, directory):
    if title == '':
        title = content.rsplit('/',1)[0].rsplit('/',1)[1]

    title = ioutils.getTitleFormated(title)
    output = '--format best --output "{dir}/{title}.%(ext)s"'.format(title = title, dir = directory)

    return downloader.download_ydl(dto, content, dto.getParameters(), output, stringReferer, [content, title, directory])


def host_animeondemand(dto, content, title, stringReferer, directory):
    parameters = dto.getParameters()
    parameters += getUserCredentials(dto, 'animeondemand')

    if 'www.' not in content:
        swap = content.split('/', 2)
        content = 'https://www.' + swap[2]

    output = getLanguage(dto, 'animeondemand')
    output += ' --output "{dir}/%(playlist)s/episode-%(playlist_index)s.%(ext)s"'

    return downloader.download_ydl(dto, content, parameters, output, stringReferer, [content, title, directory])


def host_crunchyroll(dto, content, title, stringReferer, directory):
    parameters = dto.getParameters()
    parameters += getUserCredentials(dto, 'crunchyroll')

    if 'www.' not in content:
        swap = content.split('/', 2)
        content = 'https://www.' + swap[2]

    # replace country code
    if len(content.split('/')) >= 4:
        if content.endswith('/'):
            content = content[:-1]
        pattern = "(https:\/\/www\.crunchyroll\.com\/)(.+)(\/)"
        content = re.sub(pattern, r"\1", content)

    output = getLanguage(dto, 'crunchyroll')
    output += ' --ignore-errors --output "{dir}/%(playlist)s/season-%(season_number)s-episode-%(episode_number)s-%(episode)s.%(ext)s"'.format(dir = directory)

    return downloader.download_ydl(dto, content, parameters, output, stringReferer, [content, title, directory])


def host_crunchyroll_sync(dto, content, title, stringReferer, directory):
    parameters = dto.getParameters()
    parameters += getUserCredentials(dto, 'crunchyroll')

    if 'www.' not in content:
        swap = content.split('/', 2)
        content = 'https://www.' + swap[2]

    # replace country code
    if len(content.split('/')) >= 4:
        if content.endswith('/'):
            content = content[:-1]
        pattern = "(https:\/\/www\.crunchyroll\.com\/)(.+)(\/)"
        content = re.sub(pattern, r"\1", content)

    # getting all subtitle theoretisch obsolet
    # syncOutput = '--no-mark-watched --hls-prefer-ffmpeg --socket-timeout 15'
    # syncOutput += ' --all-subs --write-sub --skip-download'
    # syncOutput += ' --ignore-errors --output "{dir}/%(playlist)s/season-%(season_number)s-episode-%(episode_number)s/subtitle-%(episode)s.%(ext)s"'.format(dir = directory)

    # download_ydl(dto, content, parameters, syncOutput, stringReferer)

    # getting all audios (low quality video) | scheinbar sind die videos unterschiedlich, also mehr als nur andere audiospur
    syncOutput = '--no-mark-watched --socket-timeout 15'
    # syncOutput += ' --hls-prefer-native'
    syncOutput += ' --hls-use-mpegts'
    syncOutput += ' --format "bestvideo[height<=480][format_id!*=hardsub][format_id!*=adaptive_hls-audio-jaJP]+bestaudio/best[height<=480][format_id!*=hardsub]"'
    syncOutput += ' --extract-audio --audio-format aac --audio-quality 0 --keep-video'
    syncOutput += ' --prefer-avconv'
    # syncOutput += ' --all-subs --write-sub'
    if dto.getOffset() > 0:
        syncOutput += ' --playlist-start %d' % dto.getOffset()
    syncOutput += ' --ignore-errors --output "{dir}/%(playlist)s/season-%(season_number)s-episode-%(episode_number)s/audio-%(autonumber)s-%(episode)s.%(ext)s"'.format(dir = directory)

    downloader.download_ydl(dto, content, parameters, syncOutput, stringReferer, [content, title, directory])

    output = '--no-mark-watched --hls-prefer-ffmpeg --socket-timeout 15'
    output += ' --format "best[format_id*=adaptive_hls-audio-jaJP][format_id!*=hardsub]"'
    # output += ' --all-subs --embed-subs'
    # output += ' --merge-output-format mkv --recode-video mkv'
    output += ' --ignore-errors --output "{dir}/%(playlist)s/season-%(season_number)s-episode-%(episode_number)s/video-%(episode)s.%(ext)s"'.format(dir = directory)

    downloader.download_ydl(dto, content, parameters, output, stringReferer, [content, title, directory])


def host_udemy(dto, content, title, stringReferer, directory):
    parameter = dto.getParameters()
    parameter += getUserCredentials(dto, 'udemy')

    if '/course/' in content:
        content = content.replace('/course', '')

    if 'https://udemy.com' in content:
        content = content.replace('https://udemy.com', 'https://www.udemy.com')

    title = content.split('/')[3]

    dto.publishLoggerDebug('udemy title: ' + str(title))
    dto.publishLoggerDebug('udemy url: ' + content)

    output = '--format best --output "{dir}/%(playlist)s - {title}/%(chapter_number)s-%(chapter)s/%(playlist_index)s-%(title)s.%(ext)s"'.format(title = title, dir = directory)

    return downloader.download_ydl(dto, content, parameter, output, stringReferer, [content, title, directory])


def host_vimeo(dto, content, title, stringReferer, directory):
    if title == '':
        title = str(input('\nPlease enter the Title:\n'))

    if stringReferer == '':
        stringReferer = str(input('\nPlease enter the reference URL:\n'))

    content = content.split('?')[0]
    title = ioutils.getTitleFormated(title)
    output = '--format best --output "{dir}/{title}.%(ext)s"'.format(title = title, dir = directory)

    return downloader.download_ydl(dto, content, dto.getParameters(), output, stringReferer, [content, title, directory])


def host_cloudfront(dto, content, title, stringReferer, directory):
    if title == '':
        title = str(input('\nPlease enter the Title:\n'))

    title = ioutils.getTitleFormated(title)
    output = '--format best --output "{dir}/{title}.mp4"'.format(title = title, dir = directory)

    return downloader.download_ydl(dto, content, dto.getParameters(), output, stringReferer, [content, title, directory])


def host_pluralsight(dto, content, title, stringReferer, directory):

    parameter = '--retries 1 --continue'
    parameter += getUserCredentials(dto, 'pluralsight')

    title = content.split('/')[5]

    dto.publishLoggerDebug('pluralsight title: ' + str(title))
    dto.publishLoggerDebug('pluralsight url: ' + content)

    if dto.getOffset() > 0:
        parameter += ' --playlist-start %d' % dto.getOffset()

    output = '--user-agent "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36 OPR/79.0.4143.50"'
    output += ' --add-header Referer:https://app.pluralsight.com/library/courses/'
    output += ' --limit-rate 0.250M --min-sleep-interval 120 --max-sleep-interval 240 --abort-on-error --format best --output "{dir}/%(playlist)s - {title}/%(chapter_number)s-%(chapter)s/%(playlist_index)s-%(title)s.%(ext)s"'.format(title = title, dir = directory)

    # print(parameter)
    # print(output)
    # os._exit(1)

    return downloader.download_ydl(dto, content, parameter, output, stringReferer, [content, title, directory])
