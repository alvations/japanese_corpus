"""
parse stuff

=== IMPORTANT PRECONDITION
Subs to be organized in a directory structure looking like this:

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



=== USAGE
   python parse_subfile.py ~/Documents/japanese_corpus/subs/


=== TODO
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
import string


SRT_TS_PATTERN = '\d{2}:\d{2}:\d{2},\d{3} --> \d{2}:\d{2}:\d{2},\d{3}'    # match timestamps in srt files
MATCH_THRESHOLD = 0.2                                                     # percent jp/en shared timestamps needed to extract subs from an srt 


def clean_ts(x):
    """cut off timestamps at the second mark, pack start & end in a tuple"""
    return re.findall('(\d{2}:\d{2}:\d{2}),\d{3} --> (\d{2}:\d{2}:\d{2}),\d{3}', x)[0]

def clean_text(x):
    """ filter and clean text"""
    x = x.strip()                     # rm leading and trailing newlines, etc
    x = re.sub('\d+$', '', x)         # remove srt sub index 
    x = x.strip()                     # chop off newly exposed newlines 
    x = re.sub('\r\n|\r|\n', ' ', x)  # join multiline subs
    x = re.sub('\<.*?\>', "", x)      # remove style tags, i.e. ""<font color="#ff0000">hello</font>""
    return x


def parse_subfile(file_path):
    """ makes { (start time, end time) : sub }  mmappings 
    """
    # .srt accounts for 95.3% (~35k files) of subs in this corpus, so i'm goign to worry about those later
    _, ext = os.path.splitext(file_path)
    if ext.lower() != '.srt':
        return

    f = open(os.path.abspath(file_path)).read()
    # this is SUCH a stupid way of doing this...sigh
    timestamps = re.findall(SRT_TS_PATTERN, f)
    captions = re.split(SRT_TS_PATTERN, f)
    captions = captions[1:]     # ignore whatever's before the first timestamp

    if len(captions) == 0:
        return None
    return {clean_ts(ts): clean_text(txt) for (ts, txt) in zip(timestamps, captions)}
    

def extract_episode_info(filename):
    """many subs belong to tv shows, etc. this tries to pull out that episode info""" 
    ep_candidates = re.findall('[^\d](\d)[^\d]|[^\d](\d\d)[^\d]', filename)

def num_shared_keys(d1, d2):
    """number of overlapping keys between two dicts"""
    return len(set(d1.keys()) & set(d2.keys()))

def is_english(s):
    """ tests whether a query string is all english characters
    """
    return all([c in string.printable for c in s])

def add_subs_for_title(subs_dict, title, jp_mapping, en_mapping):
    """ extract matching subs from a {ts => caption} mapping, and add them into the dictionary iff
        there isn't already a translation available for that timestamp
    """
    subs_dict[title].update({
            ts: (jp_caption, en_mapping[ts]) for ts, jp_caption in jp_mapping.iteritems() \
                if ( en_mapping.get(ts) and not subs_dict[title].get(ts) ) and \
                   ( len(jp_caption) > 0 and len(en_mapping[ts]) > 0 ) and \
                   ( not is_english(jp_caption) and is_english(en_mapping[ts]) )
            })


root = sys.argv[1]

# {movie title: {ts : "en sub", "jp sub"}}  mapping
SUBS = {title: {} for title in os.listdir(root)}

filetypes = defaultdict(lambda: 0)



for title in tqdm(SUBS):
    en_subs = {}
    for en_sub in os.listdir(root + '/' + title + '/en/'):
        en_mapping = parse_subfile('%s/%s/%s/%s' % (root, title, 'en', en_sub))
        if en_mapping:
            en_subs[en_sub] = en_mapping


    for jp_sub in os.listdir(root + '/' + title + '/jp/'):
        jp_mapping = parse_subfile('%s/%s/%s/%s' % (root, title, 'jp', jp_sub))
        if jp_mapping:
            # look at all complementary en sub files, sort them by % of matching subs
            ranked_matches = sorted([
                    (num_shared_keys(en_mapping, jp_mapping) / (len(jp_mapping) * 1.0), en_sub, en_mapping) \
                         for en_sub, en_mapping in en_subs.iteritems() 
                    ])

            # add in matching subs from all files above the threshold   
            for i, (percent, en_filename, en_mapping) in enumerate(ranked_matches[::-1]):
                if percent < MATCH_THRESHOLD:
                    break
                add_subs_for_title(SUBS, title, jp_mapping, en_mapping)

for t in SUBS:
    for ts in SUBS[t]:
        ID = uuid.uuid4()
        jp, en = SUBS[t][ts]
        print '%s-JP <%s>' % (ID, jp)
        print '%s-EN <%s>' % (ID, en)         
        print 

print sum(len(SUBS[t][ts]) for t in SUBS for ts in SUBS[t])







