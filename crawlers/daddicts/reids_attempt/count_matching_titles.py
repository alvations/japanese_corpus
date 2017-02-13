"""


=== USAGE
python count_matching_titles.py en_links.txt jp_links.txt
"""


import sys
import re
from fuzzywuzzy import fuzz
import os
import json

#########
#### (1) : download title listing and do soft intersection of jp/en titles
#########

def extract_title(s):
    """ extracts title from a line like
        <b><a href="http://www.d-addicts.com/forums/viewtopic.php?t=68496">100 Scene no Koi [Eng Subs] (Complete)</a></b><br>
    """
    s = re.sub('<(.*?)>|\((.*?)\)|\[(.*?)\]', '', s)
    s = s.strip()
    return s

def similarity(a, b):
    return fuzz.token_sort_ratio(a, b)

en_raw = open(sys.argv[1])
en_titles = [extract_title(l) for l in en_raw]

jp_raw = open(sys.argv[2])
jp_titles = [extract_title(l) for l in jp_raw]

matches = set(en_titles) & set(jp_titles)

en_remainder = set(en_titles) - matches
jp_remainder = set(jp_titles) - matches

extra = sorted([(similarity(en, jp), (en, jp)) for en in en_remainder for jp in jp_remainder])[::-1]
extra = extra[:150]

en_matches = list(matches)[:]
en_matches += [en for (s, (en, jp)) in extra]
en_matches = [x.lower() for x in en_matches]

jp_matches = list(matches)[:]
jp_matches += [jp for (s, (en, jp)) in extra]
jp_matches = [x.lower() for x in jp_matches]



#########
###  (2) : download denny's parsings and resolve my title list with these
#########

def get_dl_links(title, links):
    if title in links.keys():
        return links[title]
    else:
        key = max([(similarity(title, k), k) for k in links.keys()])[1]
        return links[key]

#os.system('wget https://raw.githubusercontent.com/rpryzant/japanese_corpus/master/crawlers/daddicts/download_links_en.jsonlines')
#os.system('wget https://raw.githubusercontent.com/rpryzant/japanese_corpus/master/crawlers/daddicts/download_links_ja.jsonlines')

en_titles = open('download_links_en.jsonlines')
jp_titles = open('download_links_ja.jsonlines')

dl_links_en = {json.loads(l)['info']['name']: json.loads(l) for l in en_titles}
dl_links_jp = {json.loads(l)['info']['name']: json.loads(l) for l in jp_titles}


with open('reids_dl_links_en.jsonlines', 'a') as file: 
    for title in en_matches:
        json_str = json.dumps(get_dl_links(title, dl_links_en))
        file.write(json_str + '\n')
        file.flush()


with open('reids_dl_links_jp.jsonlines', 'a') as file: 
    for title in jp_matches:
        json_str = json.dumps(get_dl_links(title, dl_links_jp))
        file.write(json_str + '\n')
        file.flush()


#print len(en_matches)
#print len(set(en_matches) & set(dl_links_en.keys()))

#print len(jp_matches)
#print len(set(jp_matches) & set(dl_links_jp.keys()))


