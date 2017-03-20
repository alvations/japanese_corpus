"""
=== DESCRIPTION
Given a corpus and score distribution, thsi file cleans the corpus
of matches below an arbitrary score threshold

=== PRECONDITION 
Generated distribution with the following:

cat daddicts_matched/distribution.txt COMMA kitsunikko_matched/distribution.txt COMMA opensubtitles_matched/distribution.txt COMMA subscene_matched/distribution.txt COMMA ted_matched/distribution.txt >> complete_distribution.txt
...and the same ordering on all the complete_en/ja subtitle files as well

=== USAGE

python sentence_selector.py [en corpusfile] [ja corpusfile] [comma-sep score distribution] [out prefix]

"""
from collections import defaultdict
import sys
import argparse
from tqdm import tqdm

LENGTH_THRESHOLD = 4

def process_command_line():
  parser = argparse.ArgumentParser(description='USAGE') # add description                                                                                                                                                                                                       
  parser.add_argument('ja_corpus', metavar='ja_corpus', type=str, help='japanese combined corpus (one phrase per line)')
  parser.add_argument('en_corpus', metavar='en_corpus', type=str, help='english combined corpus (one phrase per line)')
  parser.add_argument('scores', metavar='scores', type=str, help='score distribution (comma seperated)')

  parser.add_argument('-o', '--out_prefix', dest='output_prefix', type=str, default="out", help='prefix for output files')
  parser.add_argument('-s', '--output_size', dest='output_size', type=int, default=100000, help='top n subs to take')
  parser.add_argument('-l', '--length_threshold', dest='length_threshold', type=int, default=4, help='en length threshold on selected subs')

  args = parser.parse_args()
  return args


def main(ja_corpus, en_corpus, scores, out_prefix, output_size, length_threshold):
    score_distribution = [ float(x) for x in open(scores).read().split(',') ]

    en_out = open(out_prefix + '.en', 'w')
    ja_out = open(out_prefix + '.ja', 'w')

    d = defaultdict(list)
    total = 0
    for ei, ji, si in tqdm(zip(open(en_corpus), open(ja_corpus), score_distribution)):
        if len(ei.split()) >= length_threshold :
            d[si].append( (ei, ji)  )
            total += 1

    # select top N
    print 'seecting top ', output_size, ' from ', total
    sorted_scores = sorted(d.keys()[:])[::-1]   # move top scores to front
    sizes = map(lambda x: len(d[x]), sorted_scores)
    take_index = 0
    take_n = 0
    while take_n < output_size:
        take_n += sizes[take_index]
        take_index += 1

    # write top N to output
    print 'writing from index ', take_index, '. thats ', take_n, ' phrases.'
    i = 0
    for i, score in enumerate(sorted_scores):
      if i > take_index:   
        break
      for (ei, ji) in d[score]:
        en_out.write(ei.strip() + '\n')
        ja_out.write(ji.strip() + '\n')

    en_out.close()
    ja_out.close()


if __name__ == '__main__':
    args = process_command_line()
    main(args.ja_corpus, args.en_corpus, args.scores, args.output_prefix, args.output_size, args.length_threshold)


