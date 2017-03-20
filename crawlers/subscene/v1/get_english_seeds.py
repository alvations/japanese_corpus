"""
another gross/messy script. This one takes a list of japanese urls (data/urls/jp.txt) 
and retrieves the corresponding english urls, if they exist
"""
import sys
import os
import re
from tqdm import tqdm

jp_urls = open(sys.argv[1]).readlines()
observed = set([])
out = []
for url in tqdm(jp_urls):
    url_base = re.sub("japanese.*", "", url).strip()

    if url_base not in observed:
        try: 
            observed.add(url_base)
            os.system('wget %s -O tmp -q' % (url_base + "english"))

            os.system('grep "/english/" tmp > tmp2')
            for line in open('tmp2'):
                out.append("https://subscene.com/" + re.findall('"(.*?)"', line)[0])
        # meh 
        except:
            continue
#    else:
#        print 'seen', url_base


os.system('rm tmp')
os.system('rm tmp2')


print '\n'.join(x for x in out)
