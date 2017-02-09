"""
parse stuff

=== IMPORTANT PRECONDITIONS
1) Subs to be organized in a directory structure looking like this:

   subs_root/
      movie-1/
         en/
           english subs for movie 1
         jp/
           jp subs for movie 1
      tv-show-thats-rly-cool
         en/
           subs
         jp/
           subs
      ... 

2) Subs should have been converted to a modern character encoding, 
    preferably utf8



=== USAGE
   python parse_subfiles.py ~/Documents/kitsunekko_corpus [threshold]
   NOTE: i found a threshold of 0.2 to work well based on 35 minutes of inspection at the per-title and per-sub level for 0.1, 0.15, 0.2, and 0.25

=== TODO
short term:
    - filter out invalid matches ("Diolauge:...", longest matches, etc)
    - prioritize matches by similar names (e.g. same number episode) (or double check that same num ep is being pulled) 

longterm:
   - spellcheck on english fansubs
   - filter out non-japanese subs (post-processing?)
   - rm everything in brackets they are typically used for reporting 
     extra linguistic phenomena like  (Laughter), (Applause), (Music), (Video), etc.

"""
import sys
import os
from collections import defaultdict
import numpy as np
import re
from tqdm import tqdm
import uuid
from reconstruct import Reconstructor 
from autocorrect import spell
import string


SRT_TS_PATTERN = '\d{2}:\d{2}:\d{2},\d{3} --> \d{2}:\d{2}:\d{2},\d{3}'    # match timestamps in srt files
ASS_TS_PATTERN = '\d:\d{2}:\d{2}.\d{2},\d:\d{2}:\d{2}.\d{2}'              # match ass timestamps, i.e. '0:24:16.26,0:24:21.50'

MATCH_THRESHOLD = float(sys.argv[2])                                       # percent jp/en shared timestamps needed to extract subs from an srt 



def parse_srt(file_path):
    """ makes { (start time, end time) : sub }  mmappings from srt files
    """
    def clean_ts(x):
        """cut off timestamps at the second mark, pack start & end in a tuple"""
        return re.findall('\d(\d:\d{2}:\d{2}),\d{3} --> \d(\d:\d{2}:\d{2}),\d{3}', x)[0]

    def clean_text(x):
        """ filter and clean text"""
        x = x.strip()                     # rm leading and trailing newlines, etc
        x = re.sub('\d+$', '', x)         # remove srt sub index 
        x = x.strip()                     # chop off newly exposed newlines 
        x = re.sub('\r\n|\r|\n|\t|0000,0000,0000,\w*?,', ' ', x)  # join multiline subs
        x = re.sub('\<.*?\>', "", x)      # remove style tags, i.e. ""<font color="#ff0000">hello</font>""
        return x

    f = open(os.path.abspath(file_path)).read()
    
    timestamps = re.findall(SRT_TS_PATTERN, f)
    captions = re.split(SRT_TS_PATTERN, f)
    captions = captions[1:]     # ignore whatever's before the first timestamp

    if len(captions) == 0:
        return None
    else:
        return {clean_ts(ts): clean_text(txt) for (ts, txt) in zip(timestamps, captions)}


def parse_ass(file_path):
    """ makes { (start time, end time) : sub }  mmappings from ass files
    """
    def clean_ts(x):
        return re.findall('(\d:\d{2}:\d{2}).\d{2},(\d:\d{2}:\d{2}).\d{2}', x)[0]

    def clean_text(x):
        x = x.strip()
        x = re.sub('\N|\h|{.*?}|\\\\|\t|0000,0000,0000,\w*?,', '', x)
        return x

    f = open(file_path).readlines()
    caption_lines = [l for l in f if 'Dialogue:' in l]
    timestamps = map(lambda x: re.findall(ASS_TS_PATTERN, x)[0], caption_lines)
    captions = map(lambda x: x.split(',,')[-1].strip(), caption_lines)

    return {clean_ts(ts): clean_text(txt) for (ts, txt) in zip(timestamps, captions)}


def parse_subfile(file_path):
    """ makes { (start time, end time) : sub }  mmappings 
    """
    _, ext = os.path.splitext(file_path)
    # if something breaks, just ignore that file
    try:
        if ext.lower() == '.srt':
            return parse_srt(file_path)
        elif ext.lower() == '.ass':
            return parse_ass(file_path)
    except:
        pass
    return


def extract_episode_info(filename):
    """many subs belong to tv shows, etc. this tries to pull out that episode info""" 
    ep_candidates = re.findall('[^\d](\d)[^\d]|[^\d](\d\d)[^\d]', filename)
    return filename, ep_candidates

def num_shared_keys(d1, d2):
    """number of overlapping keys between two dicts"""
    return len(set(d1.keys()) & set(d2.keys()))

def prop_shared_keys(d1, d2):
    """proportion of overlapping keys between two dicts"""
    return num_shared_keys(d1, d2) / (len(d2) * 1.0)

def fix_spelling(s):
    """ levenschtein distance """
    x =  ' '.join(spell(w) for w in s.split())
    return x

def is_english(s):
    """ tests whether a query string is all english characters
    """
    return all([c in string.printable for c in s])

def add_subs_for_title(subs_dict, title, jp_mapping, en_title):
    """ extract matching subs from a {ts => caption} mapping, and add them into the dictionary iff
        there isn't already a translation available for that timestamp
    """
    subs_dict[title].update({
            ts: (jp_caption, en_mapping[ts]) for ts, jp_caption in jp_mapping.iteritems() \
                if en_mapping.get(ts) \
                   and not subs_dict[title].get(ts) \
                   and len(jp_caption) > 0 \
                   and len(en_mapping[ts]) > 0 \
                   and not is_english(jp_caption) \
                   and is_english(en_mapping[ts])
            })
    
def recurse_retrieve(root, *extensions):
    """ recursively searches a root directory and returns files
        that match a given extension
    """
    return [
               os.path.join(dp, f) for dp, dn, filenames in os.walk(root) \
               for f in filenames \
               if os.path.splitext(f)[1] in extensions
           ]


root = sys.argv[1]

# {movie title: {ts : "en sub", "jp sub"}}  mapping
SUBS = {title: {} for title in os.listdir(root)}

filetypes = defaultdict(lambda: 0)


for title in tqdm(SUBS):
    title_subs = {}
    en_subs = recurse_retrieve(root + '/' + title + '/en/', '.srt', '.ass')
    for en_sub in en_subs:
        en_mapping = parse_subfile(en_sub)
        if en_mapping:
            title_subs[en_sub] = en_mapping


    jp_subs = recurse_retrieve(root + '/' + title + '/jp/', '.srt', '.ass')
    for jp_sub in jp_subs:
        jp_mapping = parse_subfile(jp_sub)
        if jp_mapping:
            # look at all complementary en sub files, sort them by % of matching subs
            ranked_matches = sorted([
                    (prop_shared_keys(en_mapping, jp_mapping), en_sub, en_mapping) \
                         for en_sub, en_mapping in title_subs.iteritems() 
                    ])
            # add in matching subs from all files above the threshold
            for i, (percent, en_filename, en_mapping) in enumerate(ranked_matches[::-1]):
                if percent < MATCH_THRESHOLD:
                    break
                add_subs_for_title(SUBS, title, jp_mapping, en_mapping)

r = Reconstructor()     # RECONSTRUCT SENTANCES? IF SO WHAT CORPUS?
for t in SUBS:
    for ts in SUBS[t]:
        ID = uuid.uuid4()
        jp, en = SUBS[t][ts]
        print '%s-JP <%s>' % (ID, jp)
#        print '%s-EN <%s>' % (ID, en) 
#        print '%s-EN <%s>' % (ID, fix_spelling(r.reconstruct(en)))    # not used -- doesn't seem like fix_spelling() adds that much over reconstruct()
        print '%s-EN <%s>' % (ID, r.reconstruct(en))
        print
#        print en
#        print jp
#        print 

#print sum(len(SUBS[t][ts]) for t in SUBS for ts in SUBS[t])









