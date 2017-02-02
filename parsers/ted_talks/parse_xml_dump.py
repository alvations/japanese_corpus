"""

== xmltodict

en_dict['xml']['file'][2]['head']['talkid']     = talk id
                       ^ each file



== import xml.etree.ElementTree as ET
r[0][0][7].text        =   talk id
  ^ file



usage:
  python parse_xml_dump.py en_subs.xml jp_subs.xml


TODO: 
  - refactor
  - clean subs  (strip newlines)
  - better matching
  - filter mismatches
"""


import sys
import xmltodict
from collections import defaultdict
import re
from tqdm import tqdm
import uuid


en_xml = open(sys.argv[1])
jp_xml = open(sys.argv[2])



SUBS = defaultdict(lambda: {})


cur_talk_id = None
for line in en_xml:
    if '<talkid>' in line:
        cur_talk_id = int(re.sub('\<.*?\>', "", line))
        continue

    if '<seekvideo' in line:
        id_text = re.findall('id="(.*?)">', line)
        if len(id_text) == 0:
            continue
        caption_id = id_text[0]
        caption = re.sub('\<.*?\>', "", line)
        SUBS[cur_talk_id][caption_id] = caption.strip()


for line in jp_xml:
    if '<talkid>' in line:
        cur_talk_id = int(re.sub('\<.*?\>', "", line))
        continue

    if '<seekvideo' in line:
        id_text = re.findall('id="(.*?)">', line)
        if len(id_text) == 0:
            continue
        caption_id = id_text[0]
        caption = re.sub('\<.*?\>', "", line)
        if SUBS.get(cur_talk_id) and SUBS[cur_talk_id].get(caption_id):
            SUBS[cur_talk_id][caption_id] =  SUBS[cur_talk_id][caption_id], caption.strip()


#c = 0
for talk in SUBS:
    for ts in SUBS[talk]:
        if type(SUBS[talk][ts]) == type(tuple()):
            ID = uuid.uuid4()
#            c += 1
            en, jp = SUBS[talk][ts]
            print '%s-JP <%s>' % (ID, jp)
            print '%s-EN <%s>' % (ID, en) 
#           print en
#            print jp
            print 
#print c




