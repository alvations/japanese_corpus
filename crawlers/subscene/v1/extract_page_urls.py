"""
quick script for extracting list of subtitle resource pages from subscene search result pages

at this time its input is at: 
   data/crawled_jp_results/*
and output:
   data/seeds/jp.txt

"""
import sys
import os
import re

crawl_dir = sys.argv[1]

# extract links
os.system('find data/crawled_jp_results/ | xargs grep "/japanese" > tmp.txt')

# clean and yield links
for line in open('tmp.txt'):
    print re.findall('"(.*?)"', line)[0]

# cleanup
os.system("rm tmp.txt")

