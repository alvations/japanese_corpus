

import sys


f = sys.argv[1]

en = open(f + '.en', 'w')
ja = open(f + '.ja', 'w')

for l in open(f):
    try:
        [en_l, ja_l] = l.split('|')
        en.write(en_l + '\n')
        ja.write(ja_l.strip() + '\n')
    except:
        print l

en.close()
ja.close()

