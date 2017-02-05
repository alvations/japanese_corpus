"""
using https://wit3.fbk.eu/papers/WIT3-EAMT2012.pdf as a model, this file
filters out innapropriate alignments by discarding pairs whose length
ratio is an outlier (assuming normal distribution and 95% ci)


=== USAGE

"""
import sys
import re
import numpy as np

def parseInfo(p):
    id = p.strip().split()[0] 
    text = re.findall('<(.*?)>', p)[0]
    return id, text


def iterate_pairs(f):
    for jp_line in f:
        if 'JP' in jp_line:
            en_line = next(f)
            parseInfo(en_line)
            parseInfo(jp_line)
            yield parseInfo(jp_line), parseInfo(en_line), jp_line, en_line
        else:
            continue



parse = open(sys.argv[1])

ratios = []

for (jpId, jpTxt), (enId, enTxt), rawJp, rawEn in iterate_pairs(parse):
    if len(enTxt) == 0:    # TODO - NEED TO FIX THIS UPSTREAM
        continue
    ratios.append(len(jpTxt) * 1.0 / len(enTxt))


ratios = sorted(ratios)

N = len(ratios) * 1.0
mu = np.mean(ratios)
sd = np.std(ratios)

parse.close()  # this is dumb, TODO make cleaner
parse = open(sys.argv[1]) 
for (jpId, jpTxt), (enId, enTxt), rawJp, rawEn in iterate_pairs(parse):
    if len(enTxt) == 0:    # TODO - NEED TO FIX THIS UPSTREAM
        continue
    ratio = len(jpTxt) * 1.0 / len(enTxt)

    if (ratio <  mu - 1.96 * sd) or (ratio >  mu + 1.96 * sd):
        continue
    
    print rawJp.strip()
    print rawEn.strip()
    print 







