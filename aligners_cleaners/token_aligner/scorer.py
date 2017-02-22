 #!/usr/bin/python
 # -*- coding: utf-8 -*-

from rakutenma import RakutenMA
import json
import nltk


CONTENT_POS_TAGS = {
    # FROM https://github.com/rakuten-nlp/rakutenma
    # NOTE that this is ALL PoS tags, and non-content 
    #      tags have been commented out
    'A-c': 'adjective-common',
    'A-dp': 'adjective-dependent',
    'C': 'conjunction',
    'E': 'english word',
    'F': 'adverb',
    'I-c': 'interjection-common',
    'J-c': 'adjectival noun-common',
    'J-tari': 'adjective noun-tari',
    'J-xs': 'adjectival noun-AuxVerb stem',
#    'M-aa': 'auxiliary sign-aa',
#    'M-c': 'auxiliary sign-common',
#    'M-cp': 'auxiliary sign - open parenthesis',
    'M-p': 'auxiliary sign-period',
    'N-n': 'noun-noun',
    'N-nc': 'noun-common noun',
    'N-pn': 'noun-proper noun',
    'N-xs': 'noun-AuxVerb stem',
    'O': 'others',
    'P': 'prefix',
#    'P-fj': 'particle-adverbial',
#    'P-jj': 'partical-phrasal',
#    'P-k' 'particle-case making',
#    'P-rj': 'particle-binding',
#    'P-sj': 'particle-conjunctive',
    'Q-a': 'suffix-adjective',
    'Q-j': 'suffix-adjectival noun',
    'Q-n': 'suffix-noun',
    'Q-v': 'suffix-verb',
    'R': 'adnominal adjective',
#    'S-c': 'sign-common',
#    'S-l': 'sign-letter',
    'U': 'URL',
    'V-c': 'verb-common',
    'V-dp': 'verb-dependent',
#    'W': 'whitespace',
#    'X': 'auxVerb'
}





class PairScorer():


    def __init__(self, model):
        print model
        self.rma = RakutenMA(json.loads(open(model).read()))
        self.rma.hash_func = RakutenMA.create_hash_func(self.rma, 15)
        return


    def extract_ja_content_words(self, s):
        """ extracxts content words from a japanese sentence
            (nouns, verb roots, adjectives, no okurigana)
        """
        s = unicode(s, 'utf-8')

        for [x, y] in self.rma.tokenize(s):
            if y in CONTENT_POS_TAGS:
                print x, y
    

    def lemmatize_en_words(self, s):
        def penn_to_wordnet(pos):
            pos = pos[0].lower()
            if    pos == 'j': return 'a'
            elif  pos == 'r': return 'r'
            elif  pos == 'v': return 'v'
            else:             return 'n'

        lemmatizer = nltk.stem.WordNetLemmatizer()
        s = unicode(s, 'utf-8')
        
        for w, pos in nltk.pos_tag(nltk.word_tokenize(s)):
            print lemmatizer.lemmatize(w, pos=penn_to_wordnet(pos))



#ps = PairScorer('rakuten_model_ja.json')
ps = PairScorer('rakuten_model_ja.min.json')
f = open('test_pairs.txt')

for l in f:
    en = l.strip()
    ja = next(f).strip()
    print
    print ps.lemmatize_en_words(en)
    print ps.extract_ja_content_words(ja)






