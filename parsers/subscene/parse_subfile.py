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
   - japanese parse (+ matching)
   - filter out uninformative/broken subs
"""
import sys
import os
from collections import defaultdict
import numpy as np
import re
from tqdm import tqdm

SRT_TS_PATTERN = '\d{2}:\d{2}:\d{2},\d{3} --> \d{2}:\d{2}:\d{2},\d{3}'


def levenshtein(source, target):
    if len(source) < len(target):
        return levenshtein(target, source)

    # So now we have len(source) >= len(target).
    if len(target) == 0:
        return len(source)

    # We call tuple() to force strings to be used as sequences
    # ('c', 'a', 't', 's') - numpy uses them as values by default.
    source = np.array(tuple(source))
    target = np.array(tuple(target))

    # We use a dynamic programming algorithm, but with the
    # added optimization that we only need the last two rows
    # of the matrix.
    previous_row = np.arange(target.size + 1)
    for s in source:
        # Insertion (target grows longer than source):
        current_row = previous_row + 1

        # Substitution or matching:
        # Target and source items are aligned, and either
        # are different (cost of 1), or are the same (cost of 0).
        current_row[1:] = np.minimum(
                current_row[1:],
                np.add(previous_row[:-1], target != s))

        # Deletion (target grows shorter than source):
        current_row[1:] = np.minimum(
                current_row[1:],
                current_row[0:-1] + 1)

        previous_row = current_row

    return previous_row[-1]


def make_comparator(f):
    def compare(x, y):
        return f(x, y)

    return compare



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


def parse_subfile(file_path):
    """ makes { (start time, end time) : sub }  mmappings 
    """
    # .srt accounts for 95.3% (~35k files) of subs in this corpus, so i'm goign to worry about those later
    _, ext = os.path.splitext(file_path)
    if ext.lower() != '.srt':
        return
#    print file_path
    f = open(os.path.abspath(file_path)).read()
    
    timestamps = re.findall(SRT_TS_PATTERN, f)
    captions = re.split(SRT_TS_PATTERN, f)
    captions = captions[1:]     # ignore whatever's before the first timestamp

    if len(captions) == 0:
        return None
    else:
        return {clean_ts(ts): clean_text(txt) for (ts, txt) in zip(timestamps, captions)}

def extract_episode_info(filename):
    """many subs belong to tv shows, etc. this tries to pull out that episode info""" 
    ep_candidates = re.findall('[^\d](\d)[^\d]|[^\d](\d\d)[^\d]', filename)
    print filename, ep_candidates

def overlapping_keys(d1, d2):
    """ number of overlapping keys between two dicts"""
    return len(set(d1.keys()) & set(d2.keys()))

root = sys.argv[1]

# {movie title: subs for that title}  mapping
SUBS = {title: {'en': {}, 'jp': {}} for title in os.listdir(root)}

filetypes = defaultdict(lambda: 0)

total = 0
for title in tqdm(SUBS):
    c = 0
    title_subs = {}
    for en_sub in os.listdir(root + '/' + title + '/en/'):
        ts_caption_mapping = parse_subfile('%s/%s/%s/%s' % (root, title, 'en', en_sub))
        if ts_caption_mapping:
            title_subs[en_sub] = ts_caption_mapping


    for jp_sub in os.listdir(root + '/' + title + '/jp/'):
        ts_caption_mapping = parse_subfile('%s/%s/%s/%s' % (root, title, 'jp', jp_sub))
        if ts_caption_mapping:
            for en_sub, en_mapping in title_subs.iteritems():
                


#       for ts, caption in (ts_caption_mapping or {}).iteritems():
#            if title_subs.get(ts, None):
 
#               title_subs[ts] = title_subs[ts], caption
#                c += 1

    d = 0
    for title, pair in title_subs.iteritems():
        if type(pair) == type(tuple()):
#$            print pair[0], pair[1]
            d += 1
#    print c, d
    total += d
#    print total
    print ' ' 
print total







