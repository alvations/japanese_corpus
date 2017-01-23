"""
=== DESCRIPTION
Parses subtitle dumps from OpenSubtitles


=== USAGE (on my machine)
python parse_sub_dump.py ../../crawlers/OpenSubtitles/unparsed_sentance_pairs

"""

import sys
import re



sub_file = open(sys.argv[1])

SUBS = {}

id = 0
for line in sub_file:
    if ':lang="en"' in line:
        caption_text = re.sub('\<.*?\>', "", line).strip()
        SUBS[id] = caption_text
    elif ':lang="ja"' in line:
        caption_text = re.sub('\<.*?\>', "", line).strip()
        SUBS[id] = SUBS[id], caption_text
        id += 1

print id
