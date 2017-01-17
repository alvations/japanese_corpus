"""
Many subtitle files have weird ass encodings like SHIFT-JIS. This file should
  bring everything over to utf-8

=== Example usage:

find ~/Documents/japanese_corpus/ -type f | python correct_encodings.py

=== packages used:

https://github.com/chardet/chardet to detect encodings

$ chardetect the_pianist_disk1.srt 
>>>> the_pianist_disk1.srt: SHIFT_JIS with confidence 0.99

iconv -f SHIFT-JIS -t UTF-8 the_pianist_disk1.srt > out.txt




RIGHT NOW RUN WITH
find ~/Documents/japanese_corpus/ -type f | python correct_encodings.py







"""


import sys
import os
from tqdm import tqdm
from multiprocessing import Process


# ugly
supported_encodings = [w.upper() for l in open('supported_encodings.txt').readlines() for w in l.strip().split()]

def shellquote(s):
    return "'" + s.replace("'", "'\\''") + "'"

def correct(fp):
#    fp = shellquote(fp)
#    os.system('chardetect "%s"' % fp)
    output = os.popen('chardetect "%s"' % fp).read()
    # ugly but chardetect's output is determanistic and meh
    charset = output.split(':')[1].strip().split(' ')[0]
    print charset
    if charset.upper() in supported_encodings:
        print 'iconv -f %s -t UTF-8 "%s" > "%s"' % (charset, fp, fp + '.utf8')
        os.system('iconv -f %s -t UTF-8 "%s" > "%s"' % (charset, fp, fp + '.utf8'))
        print 'CONVERTED \n\t to "%s" \n\t encoding was: %s' % ('utf8_' + fp, charset)
    else:
        print 'SKIPPED \n\t %s \n\t encoding was: %s' % (fp, charset)

MAX_PROCESSES = 4
processes = set()
files = [line.strip() for line in sys.stdin]
#os.system('ls "/Users/rapigan/Documents/japanese_corpus/subs/oceans-thirteen/en/Ocean\'s 13 BRRip-720p[Dual-Audio][Hindi-Eng]-RedHeart.srt"')
#os.system('chardetect "/Users/rapigan/Documents/japanese_corpus/subs/oceans-thirteen/en/Ocean\'s 13 BRRip-720p[Dual-Audio][Hindi-Eng]-RedHeart.srt"')
a = "/Users/rapigan/Documents/japanese_corpus/subs/oceans-thirteen/en/Ocean's 13 BRRip-720p[Dual-Audio][Hindi-Eng]-RedHeart.srt"
correct(a)
quit()


for file in tqdm(files):
    p = Process(target=correct, args=(file,))
    p.start()
    processes.add(p)
    if len(processes) >= MAX_PROCESSES:
        os.wait()
        processes.difference_update([p for p in processes if p.is_alive()])
