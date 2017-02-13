"""


=== USAGE
python count_matching_titles.py en_links.txt jp_links.txt
"""


import sys
import re
from fuzzywuzzy import fuzz


def extract_title(s):
    """ extracts title from a line like
        <b><a href="http://www.d-addicts.com/forums/viewtopic.php?t=68496">100 Scene no Koi [Eng Subs] (Complete)</a></b><br>
    """
    s = re.sub('<(.*?)>|\((.*?)\)|\[(.*?)\]', '', s)
    s = s.strip()
    return s

def similarity(a, b):
    return fuzz.token_sort_ratio(a, b)

en_raw = open(sys.argv[1])
en_titles = [extract_title(l) for l in en_raw]

jp_raw = open(sys.argv[2])
jp_titles = [extract_title(l) for l in jp_raw]

matches = set(en_titles) & set(jp_titles)

en_remainder = set(en_titles) - matches
jp_remainder = set(jp_titles) - matches

extra = sorted([(similarity(en, jp), (en, jp)) for en in en_remainder for jp in jp_remainder])[::-1]
extra = extra[:150]

en_matches = list(matches)[:]
jp_matches = list(matches)[:]

en_matches += [en for (s, (en, jp)) in extra]
jp_matches += [jp for (s, (en, jp)) in extra]





