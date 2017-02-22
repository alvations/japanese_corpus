import sys
import re





kanji_dict = open(sys.argv[1])
for entry in kanji_dict:
    if '#' in entry: continue
    entry = entry.strip()
    kanji = entry.split()[0]
    definitions = re.findall('{(.*?)}', entry)
    for d in definitions:
        print '%s,%s' % (kanji, d)



# TODO - REFACTOR
name_dict = open(sys.argv[2])
i = 0
for entry in name_dict:
    if '#' in entry: continue
    ja_name = entry.split()[0]
    alt_name = re.findall('\[(.*?)\]', entry)
    if len(alt_name) > 0: # probably a better way to do this... 
        names = [ja_name,  alt_name[0] ]
    else:
        names = [ja_name]


    # /(o) African National Congress/ANC/   -->   ['African National Congress', 'ANC']
    # messy....
    defs = [x.strip() for y in re.findall('/(.*)/', entry) for x in y.split('/')]
    defs = [re.sub('\(\w+\)', '', x).strip() for x in defs]

    for name in names:
        for d in defs:
            print '%s,%s' % (name, d)

# TODO - GENERAL DICT - DECIDE HOW TO DO IT





print i



