"""
=== DESCRIPTION
removes duplicate entries from *sorted*  en, ja, trans files

=== USAGE
python rm_dups.py [en file] [ja corpusfile] [trans corpusfile]

"""

import sys

if len(sys.argv) < 4:
    print 
    print 'USAGE: python rm_dups.py [en file] [ja corpusfile] [trans corpusfile]'
    print
    quit()


en = sys.argv[1]
en_out = open(en + '_cleaned', 'w')

ja = sys.argv[2]
ja_out = open(ja + '_cleaned', 'w')

trans = sys.argv[3]
trans_out = open(trans + '_cleaned', 'w')

prev_en = ''
prev_ja = ''
prev_trans = ''

for en_l, ja_l, trans_l in zip(open(en), open(ja), open(trans)):
    if en_l == prev_en or ja_l == prev_ja or trans_l == prev_trans:
        continue
    else:
        en_out.write(en_l)
        ja_out.write(ja_l)
        trans_out.write(trans_l)

        prev_en = en_l
        prev_ja = ja_l
        prev_trans = trans_l
        
en_out.close()
ja_out.close()
trans_out.close()


