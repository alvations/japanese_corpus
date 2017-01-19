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



"""
import sys
import os
from collections import defaultdict
import numpy as np
import re


SRT_TS_PATTERN = '\d{2}:\d{2}:\d{2},\d{3} --> \d{2}:\d{2}:\d{2},\d{3}'


def clean_ts(x):
    """cut off timestamps at the second mark, pack start & end in a tuple"""
    return re.findall('(\d{2}:\d{2}:\d{2}),\d{3} --> (\d{2}:\d{2}:\d{2}),\d{3}', x)[0]

def clean_text(x):
    """ filter and clean text"""
    x = x.strip()                     # rm leading and trailing newlines, etc
    x = re.sub('\d+$', '', x)         # remove srt sub index 
    x = x.strip()                     # chop off newly exposed newlines 
    x = re.sub('\r\n|\r|\n', ' ', x)  # join multiline subs
    return x


def parse_en_subfile(file_path):
    """ makes { (start time, end time) : sub }  mmappings 
    """
    # .srt accounts for 95.3% (~35k files) of subs in this corpus, so i'm goign to worry about those later
    _, ext = os.path.splitext(file_path)
    if ext.lower() != '.srt':
        return
    print file_path
    f = open(os.path.abspath(file_path)).read()
    
    timestamps = re.findall(SRT_TS_PATTERN, f)
    captions = re.split(SRT_TS_PATTERN, f)
    captions = captions[1:]     # ignore whatever's before the first timestamp

    return {clean_ts(ts): clean_text(txt) for (ts, txt) in zip(timestamps, captions)}


root = sys.argv[1]

# {movie title: subs for that title}  mapping
SUBS = {title: {'en': {}, 'jp': {}} for title in os.listdir(root)}

filetypes = defaultdict(lambda: 0)


for title in SUBS:
    for en_sub in os.listdir(root + '/' + title + '/en/'):
        parse_subfile('%s/%s/en/%s' % (root, title, en_sub))

#    for jp_sub in os.listdir(root + '/' + title + '/jp/'):



