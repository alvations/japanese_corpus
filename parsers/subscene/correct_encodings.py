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


TODO: DOCUMENTAATION

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
    output = os.popen('chardetect "%s"' % fp).read()
    # ugly but chardetect's output is determanistic and meh
    charset = output.split(':')[1].strip().split(' ')[0]
    if charset.upper() in supported_encodings:
        os.system('iconv -f %s -t UTF-8 "%s" > "%s"' % (charset, fp, fp))
        print 'CONVERTED \n\t to "%s" \n\t encoding was: %s' % (fp, charset)
    else:
        print 'SKIPPED \n\t %s \n\t encoding was: %s' % (fp, charset)


if __name__ == '__main__':
    max_proc = 4
    procs = set()
    files = [line.strip() for line in sys.stdin]

    for file in tqdm(files):
        p = Process(target=correct, args=(file,))
        p.start()
        procs.add(p)
        while len(procs) >= max_proc:
            procs.difference_update([p for p in procs if not p.is_alive()])

