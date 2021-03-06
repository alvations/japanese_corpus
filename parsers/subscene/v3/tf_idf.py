import pysrt
import re
from nltk.tokenize import word_tokenize
import Stemmer
import math
from unicodedata import category

class TF_IDF():
    
    def __init__(self, subfile):
        self.subs = pysrt.open(subfile)
        self.stemmer = Stemmer.Stemmer('english')

        raw_corpus = [self.strip_punctuation(self.clean_caption(sub.text)) for sub in self.subs if len(self.clean_caption(sub.text)) > 0]
        corpus = [self.prepare_s(s) for s in raw_corpus]
        self.idf = self.inverse_document_frequency(corpus)

        self.tfidf_vecs = {}
        for raw_s, s in zip(raw_corpus, corpus):
            self.tfidf_vecs[raw_s] = self.build_tfidf_vec(s)

    def strip_punctuation(self, s):
        if type(s) is not type(u''):
            s = unicode(s, 'utf8')

        s_new = ''.join(ch for ch in s if category(ch)[0] != 'P')
        try:
            if category(s[-1])[0] == 'P':
                s_new = s_new + s[-1]
        except:
            pass
        return s_new


    def prepare_s(self, s):
        s = self.strip_punctuation(s)
        s = [self.stemmer.stemWord(w) for w in word_tokenize(s)]
        return s

    def cosine_similarity(self, v1, v2):
        def magnitude(v):
            return math.sqrt(sum([x**2 for x in v]))

        dot = sum(a*b for a,b in zip(v1, v2))
        mag = magnitude(v1) * magnitude(v2)
        if not mag:
            return 0
        return dot * 1.0 / mag


    def build_tfidf_vec(self, s):
        out = []
        for (tok, idf_val) in self.idf.items():
            tf = self.sublinear_term_frequency(tok, s)
            out.append(tf * idf_val)
        return out


    def similarity(self, ref, trans):
        try:
            trans = self.clean_caption(trans)
            ref = self.strip_punctuation(ref)
            trans = self.strip_punctuation(trans)

            ref_tfidf = self.tfidf_vecs[ref]
            trans_tfidf = self.build_tfidf_vec(self.prepare_s(trans))
            sim = self.cosine_similarity(ref_tfidf, trans_tfidf)

            return sim
        except:
            return 0

    def sublinear_term_frequency(self, tok, s):
        # todo - smothing

        count = s.count(tok)
        if count == 0:
            return 0
        return 1 + math.log(count)

    def inverse_document_frequency(self, corpus):
        idf_vals = {}
        all_tokens = set([w for s in corpus for w in s])
        for tok in all_tokens:
            contains_tok = map(lambda s: tok in s, corpus)
            idf_vals[tok] = 1 + math.log(len(corpus) * 1.0 / sum(contains_tok))
        return idf_vals

    def clean_caption(self, x):
#        x = x.text

        x = x.strip()                            # strip ends 
        x = x.lower()                            # lowercase                                                     

        ja_parens      = re.compile('\xef\xbc\x88.*?\xef\xbc\x89')
        ja_rightarrow  = re.compile('\xe2\x86\x92')
        actor          = re.compile('[\w ]+:')
        unwanted       = re.compile('[*#]')    
        brackets       = re.compile('\<.*?\>|{.*?}|\(.*?\)')
        newlines       = re.compile('\\\\n|\n')
        site_signature = re.compile('.*subtitles.*\n?|.*subs.*\n?', re.IGNORECASE)
        urls           = re.compile('www.*\s\n?|[^\s]*\. ?com\n?')
        msc            = re.compile('\\\\|\t|\\\\t|\r|\\\\r')
        encoding_error = re.compile('0000,0000,0000,\w*?')
        multi_space    = re.compile('[ ]+')

        # to and from unicode for regex to work
        x = unicode(ja_parens.sub('', x.encode('utf8')), 'utf8')
        x = unicode(ja_rightarrow.sub('', x.encode('utf8')), 'utf8')
        x = actor.sub('', x)
        x = unwanted.sub('', x)
        x = brackets.sub('', x)
        x = site_signature.sub('', x)
        x = urls.sub('', x)
        x = msc.sub('', x)
        x = encoding_error.sub('', x)
        x = newlines.sub(' ', x)
        x = multi_space.sub(' ', x)
        x = x.strip()

        return x



        




