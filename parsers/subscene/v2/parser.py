"""                                                                                                                                   
=== DESCRIPTION                                                                                                                       
takes a directory of crawled subs and produces aligned phrase pairs                                                                   
                                                                                                                                      
=== USAGE                                                                                                                             
python sub_parser.py [data_loc] [en_out] [ja_out] -t [num_threads (OPTIONAL)]                                                         
                                                                                                                                      
=== PRECONDITION                                                                                                                      
dat_loc is structured as follows:                                                                                                     
                                                                                                                                      
root/   (this is your arg)                                                                                                            
                                                                                                                                      
    title_i/                                                                                                                          
       ja/                                                                                                                            
         .srt files                                                                                                                   
       en/                                                                                                                            
         .srt files                                                                                                                   
                                                                                                                                      
    ...                                                                                                                               
"""


# coding: utf-8                                                                                                                       
from joblib import Parallel, delayed
import pysrt
import sys
import numpy as np
import string
import os
import datetime
import collections
from tqdm import tqdm
import re
import string
import argparse # option parsing                                                                                                      

# TODO - make cla                                                                                                                     
coverage_threshold = 0.85


# global dict so taht all the threads can play with it                                                                                
SUBS = {}



def process_command_line():
    """ return a tuple of args                                                                                                        
    """
    parser = argparse.ArgumentParser(description='usage')

    # positional args                                                                                                                 
    parser.add_argument('data_loc', metavar='data_loc', type=str, help='crawl output directory')
    parser.add_argument('en_out', metavar='en_out', type=str, help='en output dir')
    parser.add_argument('ja_out', metavar='ja_out', type=str, help='ja output dir')

    # optional args                                                                                                                   
    parser.add_argument('-t', '--threads', dest='num_threads', type=int, default=1, help='num threads to parse with')

    args = parser.parse_args()
    return args




def clean_caption(x):
    x = x.strip()                            # strip ends                                                                             
    x = x.lower()                            # lowercase                                                                              

    brackets       = re.compile('\<.*?\>|{.*?}|\(.*?\)')
    newlines       = re.compile('\\\\n|\n')
    site_signature = re.compile('.*subtitles.*\n?|.*subs.*\n?', re.IGNORECASE)
    urls           = re.compile('www.*\s\n?|[^\s]*\. ?com\n?')
    msc            = re.compile('\\\\|\t|\\\\t|\r|\\\\r')
    encoding_error = re.compile('0000,0000,0000,\w*?')
    multi_space    = re.compile('[ ]+')

    x = brackets.sub('', x)
    x = newlines.sub(' ', x)
    x = site_signature.sub('', x)
    x = urls.sub('', x)
    x = msc.sub('', x)
    x = encoding_error.sub('', x)
    x = multi_space.sub(' ', x)
    return x


def all_english(s):
    return all([c in string.printable for c in s])



def is_overlap(ival_a, ival_b):
    start_a, end_a = ival_a
    start_b, end_b = ival_b
    return (start_a <= start_b <= end_a) or (start_b <= start_a <= end_b)


def overlap_size(ival_a, ival_b):
    assert is_overlap(ival_a, ival_b), 'no overlap!'
    start_a, end_a = ival_a
    start_b, end_b = ival_b
    return min(end_a, end_b) - max(start_a, start_b)


def ts_caption_mapping(f):
    """ produce {(interval): caption} mapping for a file                                                                              
    """
    def sub_ival(sub):
        pivot = datetime.date(2017, 01, 01)
        return datetime.datetime.combine(pivot, sub.start.to_time()), \
               datetime.datetime.combine(pivot, sub.end.to_time())

    subs = pysrt.open(f)
    out = {}
    for sub in subs:
        if len(sub.text_without_tags) > 0:
            out[sub_ival(sub)] = clean_caption(sub.text_without_tags)
    return out



def gather_mappings(lang_dir):
    """ produce {subfile: {(interval): caption}} mappings for a directory                                                             
    """
    out = {}
    for subfile in os.listdir(lang_dir):
        out[subfile] = ts_caption_mapping(os.path.join(lang_dir, subfile))
    return out


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
        if all_english(ja_caption):
            continue

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



def align_files(title_dir, ja_sub_mappings, en_sub_mappings):
    """ align two sets of parsed .srt files, and                                                                                      
        return their matched subtitles, sorted by                                                                                     
        similarity                               
                                                                                                                                   
        returns: (score, [matches], ja srt path, en srt path)                                                                         
    """
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
    return match_candidates


def extract_matches(match_candidates):
    """ harvest aligned captions from matched srt files                                                                               
                                                                                                                                      
        returns: {                                                                                                                    
                   timestamp: {                                                                                                       
                        'ja': ja caption                                                                                              
                        'en': en caption                                                                                              
                        'overlap': timedelta                                                                                          
                     }                                                                                                                
                  }                                                                                                                   
    """
    out = {}
    i = 0
    while i < len(match_candidates) and match_candidates[i][0] > coverage_threshold:
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
    match_candidates = align_files(title_dir, ja_sub_mappings, en_sub_mappings)

    print '\t EXTRACTING BEST MATCHES...'
#    SUBS[os.path.basename(title_dir)] = extract_matches(match_candidates)                                                            
    matches = extract_matches(match_candidates)


    title = os.path.basename(title_dir)

    en = ''
    ja = ''
    for ts, caption in matches.items():
        en += caption['en'] + '\n'
        ja += caption['ja'] + '\n'
    print '\t WRITING RESULTS TO ', title + '_en_subs'
    with open(title + '_en_subs', 'w') as f:
        f.write(en.encode('utf8'))
    print '\t WRITING RESULTS TO ', title + '_ja_subs'
    with open(title + '_ja_subs', 'w') as f:
        f.write(ja.encode('utf8'))





def main(data_loc, en_out, ja_out, num_threads):
    root = data_loc
    os.system("find %s -type f -name '*.DS_Store' -delete" % root)

    Parallel(n_jobs=num_threads)(delayed(extract_subs_for_title)(os.path.join(root, title), coverage_threshold) \
                                     for title in os.listdir(root))

    print 'JOINING RESULTS...'
    split_order = []
    for f in os.listdir('.'):
        if '_subs' in f:
            split_order.append(f.split('_')[0])   # TODO - BETER SPLITTER

    en_cat = 'cat ' + ' '.join('%s_en_subs' % title for title in split_order) + ' > %s' % en_out
    ja_cat = 'cat ' + ' '.join('%s_ja_subs' % title for title in split_order) + ' > %s' % ja_out

    os.system(ja_cat)
    os.system(en_cat)


    print 'CLEANING UP...'
    os.system('rm *_subs')

    print 'DONE'

                                                                                                                                      


if __name__ == '__main__':
    args = process_command_line()
    main(args.data_loc, args.en_out, args.ja_out, args.num_threads)
