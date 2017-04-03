"""
=== DESCRIPTION
sorts en-ja caption matchings by tf-idf similarity (global term freqs across all .srt's)

=== USAGE
python subparse_sorter.py [kitsu/subscene]

"""


import numpy as np
from collections import defaultdict
from tf_idf import TF_IDF
from tqdm import tqdm
import sys

SOURCE = sys.argv[1]

#SOURCE = 'kitsu'
#SOURCE = 'subscene'

if SOURCE == 'kitsu':
    trans_f = 'kitsu_finished/trans_kitsu_cat'
    en_f = 'kitsu_finished/en_kitsu_cat'
    ja_f = 'kitsu_finished/ja_kitsu_cat'
    out_ja_f = 'out_ja_kitsu'
    out_en_f = 'out_en_kitsu'
    out_trans_f = 'out_trans_kitsu'
    idf = 'idf_kitsu'
    vec = 'vec_kitsu'
else:
    trans_f = 'subscene_finished/trans_subscene_cat'
    en_f = 'subscene_finished/en_subscene_cat'
    ja_f = 'subscene_finished/ja_subscene_cat'
    out_ja_f = 'out_ja_subscene'
    out_en_f = 'out_en_subscene'
    out_trans_f = 'out_trans_subscene'
    idf = 'idf_subscene'
    vec = 'vec_subscene'

    
#trans = open(trans_f)

#trans_corpus = [
#    l.split('|')[1].strip() for l in trans
#]

#print 'BUILDING TF-IDF VECTORS'
#tfidf = TF_IDF(trans_corpus, subfile=False)#, idf_vals='idf_test', corpus_vecs='vec_tst')
#print 'SAVING STUFF'
#tfidf.save(idf, vec)


#print 'SCORING CAPTION MATCHINGS'
#trans.close()

trans = open(trans_f)
en = open(en_f)
ja = open(ja_f)

sims = defaultdict(list)
for en_caption, ja_caption, trans_caption in tqdm(zip(en, ja, trans)):
    [sim, trans_caption] = trans_caption.split('|')
    sim = float(sim)
#    sim, _, _ = tfidf.similarity(trans_caption, en_caption)
    sims[sim].append( (en_caption, ja_caption, trans_caption) )

mu = np.mean(sims.keys())
sd = np.std(sims.keys())

print 'MU ', mu
print 'SD ', sd

sims_keys = sims.keys()[:]
sims_keys = sorted(sims_keys)

print 'WRITING TO OUTPUT'
out_ja = open(out_ja_f, 'w')
out_en = open(out_en_f, 'w')
out_trans = open(out_trans_f, 'w')
for i, s in enumerate(sims_keys):
    for (en, ja, trans) in sims[s]:
        out_ja.write(ja.strip() + '\n')
        out_en.write(en.strip() + '\n')
        out_trans.write(str(s) + '|' + trans.strip() + '\n')

