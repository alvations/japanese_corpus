"""

=== DESCRIPTION
This file takes what's essentially the HTML of a kitsunekko page 
(e.g. http://kitsunekko.net/dirlist.php?dir=subtitles%2F) after it's been grepped
for lines that contain links to sub pages. 

This script takes those files, makes a cross-language mapping from title to 
  en and jp sub urls, then steps through that dict, downloading subs as it goes
 

=== USAGE
python parse_and_match_links.py en_links.txt jp_links.txt
"""
import sys
import re
from fuzzywuzzy import fuzz
import string
import numpy as np
import collections
import os
import urllib 
import webbrowser
import time


def extract_url(html):
    """ extract url from kitsunekko html link
    """
    return re.findall('href="(.*?)"', html)[0]

def extract_title(html):
    """ extract title from kitsunekko html link
    """
    title = html.split("/strong")[0]          # hacky way of cutting out 2nd column
    title = re.sub('\<.*?\>', "", title)
    title = title.translate(None, string.punctuation).strip()   # remove punctuation
    title = title.replace(' ', '_').lower()
    return title

def generate_info(fp):
    """ generate urls and titles from a file pointer to kitunekko search page html dump
    """
    for line in fp:
        line = line.strip()
        url = extract_url(line)
        title = extract_title(line)
        yield url, title

def dl_subs(title, jp_urls, en_urls):
    """ downloads billingual subs for a title
    """
    def extract_urls(dl_page):
        os.system('wget %s -O tmp' % dl_page)
        os.system('grep "<tr><td>" tmp > tmp2')     # pull out links to sub pages
        urls = open('tmp2').read().strip()
        urls = re.findall('<a href="subtitles/(.*?)"', urls)
        for url in urls:
            url = urllib.quote(url)
            url = 'http://kitsunekko.net/subtitles/' + url
            yield url

    def inflate_and_store(lang):
        # from kitsunekko codebase: accepted fileformats are:
        #     zip, rar, 7z, ass, ssa, srt
        time.sleep(1)
        os.system('find ~/Downloads/ -name "*.zip" -exec unzip -o -d ~/Desktop/subs/%s/%s {} \;' % (title, lang))
        os.system('find ~/Downloads/ -name "*.rar" -exec unrar x -o+ {} ~/Desktop/subs/%s/%s \;' % (title, lang))
        os.system('find ~/Downloads/ -name "*.7z" -exec 7za x -o/Users/rapigan/Desktop/subs/%s/%s {} \;zxc' % (title, lang))
        os.system('rm ~/Downloads/*.zip ~/Downloads/*.rar ~/Downloads/*.7z')
        time.sleep(2)
        os.system('mv ~/Downloads/* ~/Desktop/subs/%s/%s' % (title, lang))
        os.system('rm ~/Downloads/*')

    os.system('mkdir ~/Desktop/subs/%s' % title)
    os.system('mkdir ~/Desktop/subs/%s/jp' % title)
    os.system('mkdir ~/Desktop/subs/%s/en' % title)

    for jp_sub in jp_urls:
        for url in extract_urls(jp_sub):
            webbrowser.open_new_tab(url)
            inflate_and_store('jp')

    time.sleep(2)

    for en_sub in en_urls:
        for url in extract_urls(en_sub):
            webbrowser.open_new_tab(url)
            inflate_and_store('en')

    time.sleep(1)


en_file = open(sys.argv[1])
jp_file = open(sys.argv[2])

SUBS = {}

##### build japanese half of the mapping
for (jp_url, jp_title) in generate_info(jp_file):
    SUBS[jp_title] = collections.defaultdict(list)
    SUBS[jp_title]['jp'].append(jp_url)

##### match english subs to preexisting japanese titles
#candidates = []
for (en_url, en_title) in generate_info(en_file):
    score, jp_title = sorted(map(lambda x: (fuzz.ratio(x, en_title), x), SUBS.keys()))[-1]
    if score > 81:      # see commented block below, selection based on global score distribution
        SUBS[jp_title]['en'].append(en_url)

################ take everything better than 81 (mu + .5 std)
#    - hacky but seems to work well in practice via visual inspection
#    candidates.append((score, jp_title, en_title, en_url))
#std = np.std([x[0] for x in candidates])
#mu = np.mean([x[0] for x in candidates])
#print mu, std


###### cut out titles with subs for both languages and start downloading 'em
matching_subs = [(title, urls) for (title, urls) in SUBS.iteritems() if len(urls['en']) > 0 and len(urls['jp']) > 0]

os.system('mkdir ~/Desktop/subs')

for i, (title, urls) in enumerate(matching_subs):
    if i < 365:       # got 25 titles on first night
        continue
    try:
        # close out of chrome every once in a while to give my machine AND kitsunekko a breather
        if i % 50 == 0:
            print 'RESTING'
            os.system('pkill -a -i "Google Chrome"')
            time.sleep(5)

        # skip if there ain't subs for both
        if not urls['jp'] or not urls['en']:
            continue

        dl_subs(title, urls['jp'], urls['en'])

    except Exception as e:
        print 'SOMETHING BROKE, SKIPPING...', 
        print e
        os.system('rm ~/Downloads/*')

