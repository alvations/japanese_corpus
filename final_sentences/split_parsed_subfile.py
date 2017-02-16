"""
da6cd37e-b809-40ea-a5c4-ef0472dce909-JP <jp subs>
da6cd37e-b809-40ea-a5c4-ef0472dce909-EN <No. We have to go back.>
..

Denny's matched subs look like this:
root:
  combined.en:
     No. We have to go back.
     ...
  combined.jp:   
     jp translation
     ...

this file converts reid's format into denny's format
"""

import sys
import os
import re

OUTPUT_PATH_JP = 'combined.ja'
OUTPUT_PATH_EN = 'combined.en'

input = open(sys.argv[1])
outdir = sys.argv[2]

raw_output_file_en = open(outdir + OUTPUT_PATH_EN, "w")
raw_output_file_ja = open(outdir + OUTPUT_PATH_JP, "w")


def caption_from_line(l):
    return re.findall('<(.*?)>', l)[0].replace('\n', ' ').strip()

def text_filter(ja_text, en_text):
  if len(ja_text) < 3 or len(en_text) < 5:
      return False
  return True


for line in input:
    if '-JP' in line:
        ja_text = caption_from_line(line)
        en_text = caption_from_line(next(input))

        if not text_filter(ja_text, en_text): 
            continue
        
        raw_output_file_en.write(en_text + "\n")
        raw_output_file_ja.write(ja_text + "\n")
    
raw_output_file_en.close()
raw_output_file_ja.close()
