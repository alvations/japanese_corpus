 #!/usr/bin/python
 # -*- coding: utf-8 -*-

from rakutenma import RakutenMA
import json
import nltk
from collections import defaultdict
from jpn.deinflect import guess_stem


RAKUTEN_POS_TAGS = {
    # FROM https://github.com/rakuten-nlp/rakutenma
    # NOTE that this is ALL PoS tags, and non-content 
    #      tags have been commented out
    'A-c': 'adjective-common',
    'A-dp': 'adjective-dependent',
#    'C': 'conjunction',
    'E': 'english word',
    'F': 'adverb',
#    'I-c': 'interjection-common',
    'J-c': 'adjectival noun-common',
    'J-tari': 'adjective noun-tari',
    'J-xs': 'adjectival noun-AuxVerb stem',
#    'M-aa': 'auxiliary sign-aa',
#    'M-c': 'auxiliary sign-common',
#    'M-cp': 'auxiliary sign - open parenthesis',
#    'M-p': 'auxiliary sign-period',
    'N-n': 'noun-noun',
    'N-nc': 'noun-common noun',
    'N-pn': 'noun-proper noun',
    'N-xs': 'noun-AuxVerb stem',
#    'O': 'others',
#    'P': 'prefix',
#    'P-fj': 'particle-adverbial',
#    'P-jj': 'partical-phrasal',
#    'P-k' 'particle-case making',
#    'P-rj': 'particle-binding',
#    'P-sj': 'particle-conjunctive',
#    'Q-a': 'suffix-adjective',
#    'Q-j': 'suffix-adjectival noun',
#    'Q-n': 'suffix-noun',
#    'Q-v': 'suffix-verb',
    'R': 'adnominal adjective',
#    'S-c': 'sign-common',
#    'S-l': 'sign-letter',
    'U': 'URL',
    'V-c': 'verb-common',
    'V-dp': 'verb-dependent',
#    'W': 'whitespace',
#    'X': 'auxVerb'
}



PENN_POS_TAGS = {
    # from https://www.ling.upenn.edu/courses/Fall_2003/ling001/penn_treebank_pos.html
    # non-content types have been commented out
#    'CC': 'COORDINATING CONJUNCTION',
    'CD': 'CARDINAL NUMBER',
#    'DT': 'DETERMINER',
#    'EX': 'EXISTENTIAL THERE',
    'FW': 'FOREIGN WORD',
#    'IN': 'PREPOSITION OR SUBORDINATING CONJUNCTION',
    'JJ': 'ADJECTIVE',
    'JJR': 'ADJECTIVE, COMPARATIVE',
    'JJS': 'ADJECTIVE, SUPERLATIVE',
#    'MD': 'MODAL',
    'NN': 'NOUN, SINGULAR OR MASS',
    'NNS': 'NOUN, PLURAL',
    'NNP': 'PROPER NOUN, SINMGULAR',
    'NNPS': 'PROPER NOUN, PLURAL',
#    'PDT': 'PREDETERMINER',
#    'POS': 'POSSESSIVE ENDING',
#    'PRP': 'PERSONNNAL PRONOUN',
#    'PRP$': 'POSSESSIVE PRONOUN',
    'RB': 'ADVERB',
    'RBR': 'ADVERB, COMPARATIVE',
    'RBS': 'ADVERB, SUPERLATIVE',
#    'RP': 'PARTICLE',
#    'SYM': 'SYMBOL',
#    'TO': 'TO',
#    'UH': 'INTERJECTION',
    'VB': 'VERB BASE',
    'VBD': 'VERB PAST TENSE',
    'VBG': 'VERB GERUND OR PRESENT PARTICIPLE',
    'VBN': 'VERB PAST PARTICIPLE',
    'VBP': 'VERB NON-3RD PERSON SINGULAR PRESENT',
    'VBZ': 'VERB 3RD PERSON SINGULAR PRESENT',
#    'WDT': 'WH-DETERMINER',
#    'WP': 'WP-PRONOUN',
#    'WP$': 'POSSESSIVE WH-PRONOUN',
#    'WRB': 'WH-ADVERB'
}




class Dictionary():
    def __init__(self, kv_filepath, model):
        self.rma = RakutenMA(json.loads(open(model).read()))
        self.rma.hash_func = RakutenMA.create_hash_func(self.rma, 15)


        self.ja_to_en = defaultdict(list)
        self.en_to_ja = defaultdict(list)

        for l in open(kv_filepath):
            [k, v] = l.strip().split(',')[:2]
            raw = unicode(k, 'utf-8')
#            lemma = self.rma.tokenize(raw)[0][0]
            self.ja_to_en[raw].append(v)
            self.en_to_ja[v].append(raw)
#            if not raw == lemma:
#                self.dict[lemma] = v


    def get_translations(self, en):
        return self.en_to_ja[en]

    def is_translation_pair(self, en, ja):
        return ja in self.en_to_ja[en] or \
               en in ' '.join(x for x in self.ja_to_en[ja])



class PairScorer():


    def __init__(self, model):
        print model
        self.rma = RakutenMA(json.loads(open(model).read()))
        self.rma.hash_func = RakutenMA.create_hash_func(self.rma, 15)
        return


    def extract_ja_content_lemmas(self, s):
        """ extracxts content words from a japanese sentence
            (nouns, verb roots, adjectives, no okurigana)
        """
        s = unicode(s, 'utf-8')

        out = []
        for [x, y] in self.rma.tokenize(s):
            if y in RAKUTEN_POS_TAGS:
                if y.startswith('V'):                
                    out += [(guess, y) for guess in guess_stem(x)]
                else:
                    out.append( (x, y) )
        return out

    def extract_en_content_lemmas(self, s):
        def penn_to_wordnet(pos):
            p = pos[0].lower()
            if    p == 'j': return 'a'
            elif  p == 'r': return 'r'
            elif  p == 'v': return 'v'
            else:             return 'n'

        lemmatizer = nltk.stem.WordNetLemmatizer()
        s = unicode(s, 'utf-8')
        
        out = []
        for w, pos in nltk.pos_tag(nltk.word_tokenize(s)):
            if pos in PENN_POS_TAGS:
                out.append( (lemmatizer.lemmatize(w, pos=penn_to_wordnet(pos)), pos) )
        return out



d = Dictionary('en_ja_dictionary/raw_kv_pairs', 'rakuten_model_ja.min.json')


#ps = PairScorer('rakuten_model_ja.json')
ps = PairScorer('rakuten_model_ja.min.json')
f = open('test_pairs.txt')




for l in f:
    print '======================'
    en = l.strip()
    ja = next(f).strip()
    
    en_content_lemmas = ps.extract_en_content_lemmas(en)
    for x, y in en_content_lemmas:
        print x, y


    ja_content_lemmas = ps.extract_ja_content_lemmas(ja)
    for x, y in ja_content_lemmas:
        print x, y

    i = 0
    for x, _ in en_content_lemmas:
        for y, _ in ja_content_lemmas:
            if d.is_translation_pair(x, y):
                i += 1
    print i, 'recognized translation pairs'




