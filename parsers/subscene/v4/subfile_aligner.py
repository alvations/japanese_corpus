# -*- coding: utf-8 -*-
import string
import pysrt
import re
from tqdm import tqdm
import collections
import os
from tf_idf import TF_IDF
import numpy as np
from utils import clean_caption

class Aligner():

    def __init__(self, ja_file, pair_scorer=None):
        self.ps = pair_scorer
        self.ja_file = ja_file
        self.ja = pysrt.open(ja_file)
        self.ja_start = self.first_content_caption(self.ja)
        # TODO - CLEAN UP!!
        self.ja_translations = [(self.translate(self.ja[x].text), clean_caption(self.ja[x].text)) \
                                    for x in tqdm(range(self.ja_start, min(500, len(self.ja)))) \
                                    if len(clean_caption(self.ja[x].text)) > 0 ]


    def load(self, en_file):
        self.en_file = en_file
        self.en = pysrt.open(en_file)
        self.en_start = self.first_content_caption(self.en)
        self.tf_idf = TF_IDF(en_file)        


    def first_content_caption(self, subfile):
        for i, sub in enumerate(subfile):
            if sub.start.milliseconds != 0:
                return i


    def translate(self, text):
        """ TODO - REFACTOR """
        # delete whitespace
        try:
            ja = clean_caption(text).replace(' ', '').encode('utf8')
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
                en_sub = clean_caption(self.en[j].text)
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
               


