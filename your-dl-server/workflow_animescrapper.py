# Based on https://github.com/zaini/nyaascraper

import sys
import time

import requests
from bs4 import BeautifulSoup

import your_dl_server.downloader as downloader
import your_dl_server.ioutils as ioutils


class URL:
    def __init__(self, url, ep_index, quality_index, alt_ep_index = None, alt_quality_index = None, condition = lambda x: False):
        self.url = url

        self.ep_index = ep_index
        self.quality_index = quality_index

        self.alt_ep_index = ep_index if alt_ep_index == None else alt_ep_index
        self.alt_quality_index = quality_index if alt_quality_index == None else alt_quality_index

        self.condition = condition


subsplease_url = URL('https://nyaa.si/user/subsplease?f=0&c=0_0&q={}&o=desc&p={}', -3, -2)
erairaws_url = URL('https://nyaa.si/user/Erai-raws?f=0&c=0_0&q={}&o=desc&p={}', -2, -1, -3, -2, lambda x: "[Multiple Subtitle]" in x) # condition returns True if the given row_title or content['title'] should use the alt indices
horriblesubs_url = URL('https://nyaa.si/user/HorribleSubs?f=0&c=0_0&q={}&o=desc&p={}', -2, -1)
smallsizedanimations_url = URL('https://nyaa.si/user/SmallSizedAnimations?f=0&c=0_0&q={}&o=desc&p={}', -2, -1)
akihitoSubsWeeklies_url = URL('https://nyaa.si/user/AkihitoSubsWeeklies?f=0&c=0_0&q={}&o=desc&p={}', -5, -4)

groups = {'hs' : horriblesubs_url, 'er' : erairaws_url, 'sp' : subsplease_url, 'ssa' : smallsizedanimations_url, 'asw' : akihitoSubsWeeklies_url}

base_url = 'https://nyaa.si/'


def download(dto, group, show_name, quality, start_ep, end_ep, req_file, dir, sleep_time=0.5):
    search_url = group.url.format(show_name, "{}")
    start_ep = int(start_ep)
    end_ep = int(end_ep)
    episodes_to_download = end_ep - start_ep + 1

    for page_number in range(1, 100):  # maximum page is 15 anyways
        page_url = search_url.format(page_number)
        page_html = requests.get(page_url)
        soup = BeautifulSoup(page_html.text, 'html.parser')
        rows = soup.find_all('tr', class_='success')
        if len(rows) == 0:
            rows = soup.find_all('tr', class_='danger')

        for row in rows:
            row_contents = row.findAll('a')

            links = row.find_all('td', class_='text-center')[0].find_all('a')
            magnet = base_url + links[0]['href'] if req_file else links[1]['href']
            
            for content in row_contents:
                # Checking that content being looked at is the 'a' element with the episode name
                if content.has_attr('title') and show_name.upper() in content['title'].upper():
                    row_title = content['title'].split(" ")
                    dto.publishLoggerDebug(row_title)

                    if group.condition(content['title']):
                        ep_index = group.alt_ep_index
                        quality_index = group.alt_quality_index
                    else:
                        ep_index = group.ep_index
                        quality_index = group.quality_index

                    # Checking that row is an episode to be downloaded
                    try:
                        if start_ep <= float(row_title[ep_index]) <= end_ep and quality in row_title[quality_index]:
                            dto.publishLoggerInfo("Opening: " + content['title'])
                            downloader.download_aria2c_magnet(dto, magnet, dir)
                            # os.system('dl.py -a -s -bw ' + bandwidth +  ' ydl "' + magnet + '"')
                            time.sleep(sleep_time)
                    except Exception as e:
                        # Title format is unexpected
                        dto.publishLoggerDebug(f"Did not download: {content['title']}\nError: {e}\n")
                        pass

        # Break if the actual page is not the same as page_number, meaning there are no more pages
        # Break if episodes have been downloaded
        if soup.find('li', class_='active') is None or page_number != int(soup.find('li', class_='active').text) or episodes_to_download == 0:
            break

    dto.publishLoggerDebug("Complete.")
    ioutils.elapsedTime(dto)
    if episodes_to_download > 0:
        dto.publishLoggerError("{} episode(s) could not be loaded.".format(episodes_to_download))


def usage_error(dto):
    dto.publishLoggerDebug("usage: nyaascraper.py -g <group_name> -s <show_name> -q <quality> -a <start_episode> -z <end_episode> -bw <bandwidth>\nAdd -f or "
          "--file at the end to download the .torrent files instead of open magnets\n"
          "If you don't give a group name, Erai-raws is used by default.\n"
          "er = Erai-raws, hs = horriblesubs, sp = subsplease, ssa = smallsizedanimations")
    sys.exit(2)


def anime(dto, group_name, show_name, quality, start_ep, end_ep, req_file, dir):
    download(dto, groups.get(group_name, groups['er']), show_name, quality, start_ep, end_ep, req_file, dir)
