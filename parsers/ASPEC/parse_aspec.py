
"""
=== DESCRIPTION
This script takes an ASPEC corpus file as input, and produces 
  tokenized monolingual corpus files as output

=== USAGE
python parse_aspec.py [input file] [ja parser model]
"""
from rakutenma import RakutenMA
import sys
import os
import codecs
import json
from joblib import Parallel, delayed






model = 'rakuten_model_ja.min.json' if len(sys.argv) <= 3 else sys.argv[2]


def process(f):
    suffix = f.split('.')[-1]
    input = open('split_files/' + f)

    # bulid tokenizers
    ja_tokenizer = RakutenMA(json.loads(open(model).read()))
    ja_tokenizer.hash_func = RakutenMA.create_hash_func(ja_tokenizer, 15)


    en_outfile = codecs.open('tokenized/en_tmp.' + suffix, 'w', 'utf-8') 
    ja_outfile = codecs.open('tokenized/ja.' + suffix, 'w', 'utf-8')

    # parse en/ja lines, tokenize ja with rakuten
    en_lines = []
    ja_lines = []
    for i, line in enumerate(input):
        if i % 10000 == 0:  print i

        [similarity, id, _, ja, en] = line.split('|||')
        en_outfile.write(' '.join(x for x in en.lower().strip().decode('utf-8').split()) + '\n')
        ja_outfile.write(' '.join([x[0] for x in ja_tokenizer.tokenize(ja.strip().decode('utf-8'))]) + '\n')

    en_outfile.close()
    ja_outfile.close()


    # tokenize en with moses
    os.system('perl moses_tokenizer.perl -l en -threads 8 < %s > %s' % ('tokenized/en_tmp.' + suffix, 'tokenized/en.' + suffix))




os.system('rm -r split_files; mkdir split_files')
os.system('rm -r tokenized; mkdir tokenized')
os.system('split -l 50000 %s split_files/train.' % sys.argv[1])



Parallel(n_jobs=4)(delayed(process)(f) for f in os.listdir('split_files/') if f.startswith('train.'))
