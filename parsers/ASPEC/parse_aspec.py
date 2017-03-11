
"""
=== DESCRIPTION
This script takes an ASPEC corpus file as input, and produces 
  tokenized monolingual corpus files as output

=== USAGE
python parse_aspec.py [input file] [en output] [ja output]
"""
from rakutenma import RakutenMA
from nltk.tokenize.moses import MosesTokenizer
import sys
import os
import codecs
import json

input = open(sys.argv[1])
en_out = sys.argv[2]
ja_out = sys.argv[3]
model = sys.argv[4] if len(sys.argv) == 4 else 'rakuten_model_ja.min.json'


# bulid tokenizers
ja_tokenizer = RakutenMA(json.loads(open(model).read()))
ja_tokenizer.hash_func = RakutenMA.create_hash_func(ja_tokenizer, 15)
en_tokenizer = MosesTokenizer()


en_outfile = codecs.open('tmp', 'w', 'utf-8') 
ja_outfile = codecs.open(ja_out, 'w', 'utf-8')

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
os.system('perl moses_tokenizer.perl -l en -threads 8 < tmp > %s' % en_out)


