# -*- coding: utf-8 -*-
import string
import pysrt
import re
from tqdm import tqdm
import collections
import os
from tf_idf import TF_IDF
import numpy as np

class Aligner():

    def __init__(self, ja_file, pair_scorer=None):
        self.ps = pair_scorer
        self.ja_file = ja_file
        self.ja = pysrt.open(ja_file)
        self.ja_start = self.first_content_caption(self.ja)
        # TODO - CLEAN UP!!
        self.ja_translations = [(self.translate(self.ja[x].text), self.clean_caption(self.ja[x].text)) \
                                    for x in tqdm(range(self.ja_start, min(500, len(self.ja)))) \
                                    if len(self.clean_caption(self.ja[x].text)) > 0 ]


    def load(self, en_file):
        self.en_file = en_file
        self.en = pysrt.open(en_file)
        self.en_start = self.first_content_caption(self.en)
        self.tf_idf = TF_IDF(en_file)        


    def first_content_caption(self, subfile):
        for i, sub in enumerate(subfile):
            if sub.start.milliseconds != 0:
                return i



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



    def score_pair(self, i, j):
        ja_s = self.clean_caption(self.ja[i])
        en_s = self.clean_caption(self.en[j])
        
        dictionary_score = self.ps.score_v2(en_s, ja_s)
        closeness_score = -0.05 * abs(i-j)**2
        
        return dictionary_score + closeness_score



    def forward_pass(self):
        D = collections.defaultdict(lambda: (-10, (0, 0)))
        
        delta = len(self.ja) - len(self.en)
        print 'DELTA ', delta

        for i in range(self.ja_start, len(self.ja)):
            D[i, self.en_start] = (0, (i, self.en_start))
        for j in range(self.en_start, len(self.en)):
            D[self.ja_start, j] = (0, (i, self.en_start))
        
        en_min = self.en_start+1

        for i in tqdm(range(self.ja_start+1, len(self.ja))):
            old_min = en_min
            for j in range(en_min, len(self.en)):
                print i, j
                D[i, j] = max(
                    (D[i-1, j-1][0] + self.score_pair(i, j), (i-1, j-1) ),
                    (D[i-1, j][0],                           (i-1, j)   ),
                    (D[i, j-1][0],                           (i, j-1)   )
                    )
                # if consumed an en, move the min up
                if D[i,j][1] == (i-1, j-1) and en_min == old_min:
                    en_min += 1

                if abs(i - j) > (abs(delta) + 5):
                    break
        print D
        return D


    def traceback(self, D):
        i = len(self.ja) - 1
        j = len(self.en) - 1

        alignments = []
        while i > self.ja_start and j > self.en_start:
            score, (from_i, from_j) = D[i,j]
            if from_i == i-1 and from_j == j-1:
                alignments.append((from_i, from_j))
            i = from_i
            j = from_j

        return alignments


    def get_pairs(self, alignments):
        converter = lambda (i, j): (self.clean_caption(self.ja[i]), self.clean_caption(self.en[j])) 
        pairs = map(converter, alignments)
        return pairs


    def solve(self):
        """ dp matching """
        D = self.forward_pass()
        alignments = self.traceback(D)
        matched_pairs = self.get_pairs(alignments)
        return matched_pairs


    def clean(self, ja_i, en_i):
        return self.clean_caption(self.ja[ja_i]), self.clean_caption(self.en[en_i])


    def solve_v2(self):
        """ scorer local matching """
        i = self.ja_start
        j = self.en_start

        delta = abs(len(self.ja) - len(self.en))

        while i < len(self.ja) and j < len(self.en):
            candidates = sorted([(self.score_pair(i, jprime), (i, jprime), self.clean(i, jprime)) for jprime in range(j, j+delta)])[::-1]
            score, (i, j), (ja_s, en_s) = candidates[0]
            yield score, i, j, ja_s, en_s, candidates
            i += 1
            j += 1


    def translate(self, text):
        """ TODO - REFACTOR """
        # delete whitespace
        try:
            ja = self.clean_caption(text).replace(' ', '').encode('utf8')
            ja = ja.replace('\xe3\x80\x80', '')
            ja = ja.strip()
            if len(ja) == 0:
                return None
            # get trans
            cmd = "./trans ja: " + ja
    #        print cmd
            result = os.popen(cmd).read().split('\n')[-2].split(',')[0]

            # parse trans
    #        result = result.encode('ascii')
            result = ''.join([char for char in result if char in string.printable])
            result = result[7:-4].lower()
        except: 
            result = ''
        return result


    def solve_v3(self): 
        """ tf-idf translation matching """
        j = self.ja_start
        e = self.en_start

        delta = (abs((len(self.ja) - j) - (len(self.en) - e)))


        matches = []
        for i, (trans, ja_sub) in enumerate(self.ja_translations):
            print '\t\t i ', i, len(self.ja_translations)

            if e+i > len(self.en):
                break
            candidates = []
            for j in range(e+i, min(len(self.en), e+i+delta)):
                en_sub = self.clean_caption(self.en[j].text)
                sim =  self.tf_idf.similarity(en_sub, trans)
                subs = (en_sub, ja_sub)
                candidates.append( (sim, j, subs, trans) )
            candidates = sorted(candidates)[::-1]
            if len(candidates) > 0:
                matches.append(candidates[0])

#        print 'matches len ', len(matches)
#        print 'm0 ', matches[0]
        len_ratios = [len(m[2][0]) * 1.0 / len(m[2][1]) for m in matches]
        ratio_mean = np.mean(len_ratios)
        ratio_std = np.std(len_ratios)
        ratio_cuttoff = ratio_mean + ratio_std

        sims = [m[0] for m in matches]
        sim_mean = np.mean(sims)
        sim_std = np.std(sims)
        sim_cutoff = sim_mean + (0.25 * sim_std)

        print 'SPEWING MATCHES FOR', self.ja_file, self.en_file
        for match in matches:
#            print 'match ', match
            sim, e, (en, ja), trans = match

            len_ratio = len(en) * 1.0 / len(ja)

            if sim > sim_cutoff and len_ratio < ratio_cuttoff:
                yield en, ja
#                print en
#                print ja
#                print trans
#                print sim
#                print

            
#            sim, (e_new, j_new), (ja_s, en_s) = candidates[-1]

#            print sim
#            print e_new, j_new
#            print ja_s
#            print en_s
#            print
               


