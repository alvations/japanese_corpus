import pysrt
import re
import nltk
nltk.data.path.append('/atlas/u/rpryzant/subscene/subs')    # for atlas
from nltk.tokenize import word_tokenize
import Stemmer
import math
from utils import clean_caption
from unicodedata import category
import collections


class TF_IDF():
    def __init__(self, subfile):
        self.subs = pysrt.open(subfile)
        self.stemmer = Stemmer.Stemmer('english')

        corpus = self.prepare_corpus()

        self.idf = self.inverse_document_frequency(corpus)

        self.tfidf_vecs = {}
        for s in corpus:
            self.tfidf_vecs[''.join(w for w in s)] = self.build_tfidf_vec(s)


    def prepare_corpus(self):
        """ preps corpus for tf-idf:
              - clean captions
              - strip of nonterminal punctuation
              - stem words
              
            returns: [ [words] ]
        """
        out_raw = []
        out = []
        for sub in self.subs:
            caption = clean_caption(sub.text)
            if len(caption) == 0:
                continue
            out.append(self.prep_cleaned_caption(caption))
        return out


    def prep_cleaned_caption(self, s):
        """ strips punctation and stems worsd
        """
        # strip nonterminal punctuation
        if type(s) is not type(u''):
            s = unicode(s, 'utf8')
        s_new = ''.join(ch for ch in s if category(ch)[0] != 'P')
        try:
            if category(s[-1])[0] == 'P':
                s_new = s_new + s[-1]
        except:
            pass

        # stem words
        s_new = [self.stemmer.stemWord(w) for w in word_tokenize(s_new)]
        return s


    def cosine_similarity(self, v1, v2):
        """ cosine similarity: v1 * v2 / |v1| |v2}
        """
        def magnitude(v):
            return math.sqrt(sum([x**2 for x in v]))

        dot = sum(a*b for a,b in zip(v1, v2))
        if not dot:   # short circuit 
            return 0
        mag = magnitude(v1) * magnitude(v2)
        if not mag:
            return 0
        return dot * 1.0 / mag


    def build_tfidf_vec(self, s):
        """ builds a tf-idf vector for a sentance s
        """
        word_freqs = collections.Counter(s)
        
        # todo - list comprehension might be a hair faster?
        out = []
        for (tok, idf_val) in self.idf.items():
            tf = (1 + math.log(word_freqs[tok])) if word_freqs[tok] else 0
            out.append(tf * idf_val)
        return out


    def similarity(self, ref, trans):
        """ tf-idf similarity for two sentences.
             ref: [ [words] ], in corpus, PRECONDITION: cleaned
             trans: [ [words] ], to be compared, PRECONDITION: unclean
        """
        try:
            ref = self.prep_cleaned_caption(ref)

            trans = clean_caption(trans)
            trans = self.prep_cleaned_caption(trans)

            ref_tfidf = self.tfidf_vecs[''.join(w for w in ref)]
            trans_tfidf = self.build_tfidf_vec(trans)
            return self.cosine_similarity(ref_tfidf, trans_tfidf)

        except:
            return 0


    def inverse_document_frequency(self, corpus):
        """ the "idf" part of tf-idf
        """
        idf_vals = {}
        all_tokens = set([w for s in corpus for w in s])
        for tok in all_tokens:
            contains_tok = map(lambda s: tok in s, corpus)
            idf_vals[tok] = 1 + math.log(len(corpus) * 1.0 / sum(contains_tok))
        return idf_vals

