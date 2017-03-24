
# coding: utf-8

# In[2]:

import pysrt
import sys
import numpy as np
import string
import os
import datetime
import collections
from tqdm import tqdm


# In[3]:


def is_overlap(ival_a, ival_b):
    start_a, end_a = ival_a
    start_b, end_b = ival_b
    return (start_a <= start_b <= end_a) or (start_b <= start_a <= end_b)


def overlap_size(ival_a, ival_b):
    assert is_overlap(ival_a, ival_b), 'no overlap!'
    start_a, end_a = ival_a
    start_b, end_b = ival_b
    return min(end_a, end_b) - max(start_a, start_b)


def score_and_match(ja_ts_map, en_ts_map):
    """ match up two {(ts): caption} mappings and score them
    
        each match is of the form:
        {
            ja_ival: {
                ja_caption: "...",
                en_matches: [
                    {
                        ival: en_ival,
                        caption: "...",
                        overlap: ...
                    }
                ]
            } 
        }
    """
    ja_matches = 0
    matches = {}
    for ja_ival, ja_caption in ja_ts_map.items():
        matches[ja_ival] = {
            'ja_caption': ja_caption,
            'en_matches': []
        }

        caption_match = False
        for en_ival, en_caption in en_ts_map.items():
            if is_overlap(ja_ival, en_ival):
                matches[ja_ival]['en_matches'].append({
                    'ival': en_ival,
                    'caption': en_caption,
                    'overlap': overlap_size(en_ival, ja_ival)
                })
                caption_match = True
        ja_matches = ja_matches + (1 if caption_match else 0)

    return ja_matches * 1.0 / len(ja_ts_map), matches


def ts_caption_mapping(f):
    """ produce {(interval): caption} mapping for a file
    """
    def sub_ival(sub):
        pivot = datetime.date(2017, 01, 01)
        return datetime.datetime.combine(pivot, sub.start.to_time()),                datetime.datetime.combine(pivot, sub.end.to_time())
    
    subs = pysrt.open(f)
    out = {}
    for sub in subs:
        out[sub_ival(sub)] = sub.text_without_tags
    return out


def gather_mappings(lang_dir):
    """ produce {subfile: {(interval): caption}} mappings for a directory
    """
    out = {}
    for subfile in os.listdir(lang_dir):
        out[subfile] = ts_caption_mapping(os.path.join(lang_dir, subfile))
    return out


def extract_subs_for_title(title_dir, coverage_threshold):
    """ parse and align subs for a title
    
        precondition:
            title_dir/
                en/
                    en .srt files
                ja/
                    ja .srt files
    """
    print 'STARTING ', title_dir
    
    print '\t PARSING .srt FILES...'
    ja_sub_mappings = gather_mappings(os.path.join(title_dir, 'ja'))
    en_sub_mappings = gather_mappings(os.path.join(title_dir, 'en'))
    
    print '\t ALIGNING SUBS...'
    match_candidates = []
    for (ja_title, ja_subs) in ja_sub_mappings.items():
        for (en_title, en_subs) in en_sub_mappings.items():
            coverage, matches = score_and_match(ja_subs, en_subs)
            match_candidates.append( (
                coverage,
                matches,
                os.path.join(title_dir, 'ja', ja_title),
                os.path.join(title_dir, 'en', en_title),
            ) )
    match_candidates = sorted(match_candidates)[::-1]

    print '\t EXTRACTING BEST MATCHES...'
    out = {}
    i = 0
    while match_candidates[i][0] > coverage_threshold:
        print '\t\t working on file ', i
        coverage, matches, ja_path, en_path = match_candidates[i]
        for ja_ival, match in matches.items():
            ja_caption = match['ja_caption']
            
            if len(match['en_matches']) == 0: continue
            
            en_captions = sorted(match['en_matches'], key=lambda x: x['overlap'])[::-1]
            # TODO - take best, not first?
            if not ja_ival in out:
                out[ja_ival] = {
                    'ja': ja_caption,
                    'en': en_captions[0]['caption'],
                    'overlap': en_captions[0]['overlap']
                 }
        i += 1
    return out


# In[4]:

root = 'out'

os.system("find %s -type f -name '*.DS_Store' -delete" % root)

SUBS = {title: {} for title in os.listdir(root)}

coverage_threshold = 0.85

for title in os.listdir(root):
    SUBS[title] = extract_subs_for_title(os.path.join(root, title), coverage_threshold)
    
for title, ts_caption_mapping in SUBS.items():
    for ts, caption in ts_caption_mapping.items():
        pass
#        print caption
#        print caption['ja']
#        print caption['en']
#        print


# In[ ]:



