"""

=== DESCRIPTION
This file takes what's essentially the HTML of a kitsunekko page 
(e.g. http://kitsunekko.net/dirlist.php?dir=subtitles%2F) after it's been grepped
for lines that contain links to sub pages. 

This script takes those files, makes a cross-language mapping from title to 
  en and jp sub urls, then steps through that dict, downloading subs as it goes
 

=== USAGE
python parse_and_match_links.py en_links.txt jp_links.txt


TODO
 - finish up organization
 - dl



"""
import sys
import re
from fuzzywuzzy import fuzz
import string
import numpy as np
import collections


en_file = open(sys.argv[1])
jp_file = open(sys.argv[2])

SUBS = {}

for line in jp_file:
    # extract and clean url, title
    line = line.strip()
    url = re.findall('href="(.*?)"', line)[0]
    title = line.split("/strong")[0]          # hacky way of cutting out 2nd column
    title = re.sub('\<.*?\>', "", title)
    title = title.translate(None, string.punctuation).strip()   # remove punctuation
    title = title.replace(' ', '_').lower()
    SUBS[title] = collections.defaultdict(list)
    SUBS[title]['jp'].append(url)

#candidates = []
for line in en_file:
    # extract and clean url, title
    line = line.strip()
    en_url = re.findall('href="(.*?)"', line)[0]
    en_title = line.split("/strong")[0]          # again, cut out 2nd col
    en_title = re.sub('\<.*?\>', "", en_title)
    en_title = en_title.translate(None, string.punctuation).strip()   # remove punctuation
    en_title = en_title.replace(' ', '_').lower()

    score, jp_title =  sorted(map(lambda x: (fuzz.ratio(x, en_title), x), SUBS.keys()))[-1]
    if score > 81:      # see commented block below
        SUBS[jp_title]['en'].append(en_url)

################ take everything better than 81 (mu + .5 std)
#    - hacky but seems to work well in practice via visual inspection
#    candidates.append((score, jp_title, en_title, en_url))
#std = np.std([x[0] for x in candidates])
#mu = np.mean([x[0] for x in candidates])
#print mu, std

c = 0
for jp_title, urls in SUBS.iteritems():
    if type(urls) == type(tuple()):
        print urls
        c += 1

print c
