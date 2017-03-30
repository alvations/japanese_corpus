"""                                                                                                                                   
=== DESCRIPTION
 a directory of crawled subs and produces aligned phrase pairs

=== USAGE                                                                                                                            
python parser.py [data_loc] [en_out] [ja_out] -t [num_threads (OPTIONAL)]                                                        
                                                                                                                                     
=== PRECONDITION
_loc is structured as follows:                                                                                                     
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
from guessit import guessit
from difflib import SequenceMatcher
from scorer import PairScorer
from subfile_aligner import Aligner

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
    
    ja_parens      = re.compile('\xef\xbc\x88.*?\xef\xbc\x89')
    ja_rightarrow  = re.compile('\xe2\x86\x92')
    actor          = re.compile('[\w ]+:')
    unwanted       = re.compile('[*#]')    
    brackets       = re.compile('\<.*?\>|{.*?}|\(.*?\)')
    newlines       = re.compile('\\\\n|\n')
    site_signature = re.compile('.*subtitles.*\n?|.*subs.*\n?', re.IGNORECASE)
    urls           = re.compile('www.*\s\n?|[^\s]*\. ?com\n?')
    msc            = re.compile('\\\\|\t|\\\\t|\r|\\\\r')
    encoding_error = re.compile('0000,0000,0000,\w*?')
    multi_space    = re.compile('[ ]+')

    x = ja_parens.sub('', x)
    x = ja_rightarrow.sub('', x)
    x = actor.sub('', x)
    x = unwanted.sub('', x)
    x = brackets.sub('', x)
    x = site_signature.sub('', x)
    x = urls.sub('', x)
    x = msc.sub('', x)
    x = encoding_error.sub('', x)
    x = newlines.sub(' ', x)
    x = multi_space.sub(' ', x)
    x = x.strip()
    return x



def mostly_english(s):
    return (sum([1 if c in string.printable else 0 for c in s]) * 1.0 / len(s)) > 0.5



def should_align(ja_f, en_f):
    """ some title-based heuristics on whether a title should match
        TODO - REFACTOR

    """
    def similarity(a, b):
        if not a or not b or len(a) == 0 or len(b) == 0:
            return 0
        return SequenceMatcher(None, a, b).ratio()

    def report(b):
        print b
        print ja_f
        print en_f


    ja = guessit(ja_f)
    en = guessit(en_f)

    if ja.get('title') and en.get('title') and \
            similarity(ja.get('title'), en.get('title')) < 0.5:
#        report(False)
        return False

    if ja.get('type') == 'movie' and en.get('type') == 'movie':
        if similarity(ja.get('title'), en.get('title')) > 0.8 and \
           similarity(ja.get('alternative_title'), en.get('alternative_title')) > 0.9:
#            report(True)
            return True

    if ja.get('type') == 'episode' and en.get('type') == 'episode':
        if ja.get('episode') == en.get('episode') or \
                similarity(ja.get('episode_title'), en.get('episode_title')) > 0.9:
#            report(True)
            return True

    return False
        


def get_file_alignments(ja_title_root, en_title_root):
    alignments = collections.defaultdict(list)
    for ja_subfile in os.listdir(ja_title_root):
        for en_subfile in os.listdir(en_title_root):
            if should_align(ja_subfile, en_subfile):
                alignments[os.path.join(ja_title_root, ja_subfile)].append(
                    os.path.join(en_title_root, en_subfile))
    return alignments


def en_content_words(ja):
    """ uses py-translate (https://pypi.python.org/pypi/py-translate/)
        to do dictionary lookups for all the words in a ja sentence, then
        reduces it to content words
    """
    def translate_words():
        cmd = u"translate ja en <<< '" + ja + "'"
        words = os.popen(cmd.encode('utf8')).read().split()
        return words

    words = translate_words()


def get_first_content_caption_index(subs):
    for i, sub in enumerate(subs):
        if sub.start.milliseconds != 0:
            return i


def harvest_captions(ja_subfile, en_subfiles, ps):
    
    a = Aligner(ps, ja_subfile)

    for en_subfile in en_subfiles:
        print '\t MATCHING WITH ', en_subfile
        a.load(en_subfile)
        out = []
        for pair in tqdm(a.solve_v3()):
            print 'ADDING PAIR ', pair
            out.append(pair)
    return out


def harvest_captions_DEPRECIATED(ja_subfile, en_subfile, ps):
    def overlaps(a, b):
        return (a.start <= b.start <= a.end) or (b.start <= a.start <= b.end)

    def overlap_size(a, b):
        return min(a.end, b.end) - max(a.start, b.start)
    
    for score, i, j, ja_s, en_s, rejected in a.solve_v2():
        print ja_s
        print en_s
        print i, j
        print score
        print rejected
        print

#    soln = a.solve()
    ja_subs = pysrt.open(ja_subfile)
    en_subs = pysrt.open(en_subfile)

    ja_i = get_first_content_caption_index(ja_subs)
    en_i = get_first_content_caption_index(en_subs)

    offset = ja_subs[ja_i].start - en_subs[en_i].start

    en_subs.shift(hours=offset.hours,
                  minutes=offset.minutes,
                  seconds=offset.seconds,
                  milliseconds=offset.milliseconds)

    matches = collections.defaultdict(list)

    # TODO - FIGURE THIS OUT
    # idea: step through both at a time, when gets knocked out of alignment,
    # use scorer to scan for next appropriate alignemnt and re-shift
    for j in range(ja_i, len(ja_subs)):
        for e in range(en_i, len(en_subs)):
            if overlaps(ja_subs[j], en_subs[e]):
                matches[clean_caption(ja_subs[j].text)].append( 
                    (overlap_size(ja_subs[j], en_subs[e]), ja_subs[j].start, j, en_subs[e].start, e, clean_caption(en_subs[e].text)) 
                    )

    for ja_caption, en_matches in matches.items():
        print ja_caption
        print [m for m in sorted(en_matches)]
        print 
    print '=======================KNOWCKED OUT'


def get_caption_alignments(file_alignments, ps):
    out = []
    for (ja_subfile, en_matches) in file_alignments.items():
        print '\t HARVESTING FOR ', ja_subfile
        alignments = harvest_captions(ja_subfile, en_matches, ps)
        out = out + alignments
    return out


def extract_subs(ja, ens, title, coverage_threshold):
    """ parse and align subs for a pair of srt files
    """

    print '\t BUILDING ALIGNER FOR...', ja
    a = Aligner(ja)
    print '\t ALIGNER BUILT...', ja

    print '\t JA PIVOT ', ja
    for en_subfile in ens:
        print '\t MATCHING WITH ', en_subfile
        a.load(en_subfile)
        alignments = []
        for pair in tqdm(a.solve_v3()):
            alignments.append(pair)
    
    en = ''
    ja = ''
    for en_s, ja_s in aligned_captions:
        en += en_s + '\n'
        ja += ja_s + '\n'
    print '\t WRITING RESULTS TO ', title + '_en_subs'
    with open(title + '_en_subs', 'a') as f:
        f.write(en.encode('utf8'))
    print '\t WRITING RESULTS TO ', title + '_ja_subs'
    with open(title + '_ja_subs', 'a') as f:
        f.write(ja.encode('utf8'))


def generate_subfiles(root_dir):
    """ spits out ja files and aligned en files
    """
    for title_dir in os.listdir(root_dir):
        print 'ALIGNING ', title_dir
        file_alignments = get_file_alignments(os.path.join(root_dir, title_dir, 'ja'),
                                              os.path.join(root_dir, title_dir, 'en'))
        print 'ALIGNMENT DONE ', title_dir
        for ja_filename, en_filenames in file_alignments.items():
            yield ja_filename, en_filenames, title_dir


def main(data_loc, en_out, ja_out, num_threads):
    root = data_loc
    os.system("find %s -type f -name '*.DS_Store' -delete" % root)

    Parallel(n_jobs=num_threads)(delayed(extract_subs)(ja, ens, title, coverage_threshold) \
                                     for (ja, ens, title) in generate_subfiles(data_loc))

    # Parallel makes its own namespace, so i couldn't modify a shared
    # dictionary or anything. had to split and join.
    print 'JOINING RESULTS...'
    split_order = []
    for f in os.listdir('.'):
        if '_en_subs' in f:
            split_order.append(f.split('_')[0])   # TODO - BETER SPLITTER

    en_cat = 'cat ' + ' '.join('%s_en_subs' % title for title in split_order) + ' > %s' % en_out
    ja_cat = 'cat ' + ' '.join('%s_ja_subs' % title for title in split_order) + ' > %s' % ja_out

    print ja_cat
    os.system(ja_cat)

    print en_cat
    os.system(en_cat)


#    print 'CLEANING UP...'
#    os.system('rm *_subs')

    print 'DONE'

                                                                                                                                     
if __name__ == '__main__':
    args = process_command_line()
    main(args.data_loc, args.en_out, args.ja_out, args.num_threads)
