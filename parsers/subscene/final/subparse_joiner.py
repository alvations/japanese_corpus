
# coding: utf-8

# In[12]:

"""
This file takes the output of  * parser_v4.py * and
performs the joining step at its end because joins don't
quite work over multiple machines.

"""


# In[6]:

import sys
import os
from tqdm import tqdm


# In[7]:

def file_length(f):
    try:
        return int(os.popen('wc -l %s' % f).read().strip().split()[0])
    except Exception as e:
        print f
        print e


# In[8]:

os.listdir('.')


# In[11]:

# target_dir = 'KITSU_PARSE'
target_dir = 'SUBSCENE_PARSE'




split_order = []
for f in os.listdir(target_dir):
    if 'en_subs' in f:
        split_order.append(f.split('_')[0])

i = 0
en_cat = 'cat'
ja_cat = 'cat'
trans_cat = 'cat '
for title in tqdm(split_order):
    ja = os.path.join(target_dir, title) + '_ja_subs'
    en = os.path.join(target_dir, title) + '_en_subs'
    trans = os.path.join(target_dir, title) + '_trans_subs'
#    print ja
    if os.path.exists(ja) and          os.path.exists(en) and         os.path.exists(trans) and         (file_length(ja) == file_length(en) == file_length(trans)):
            i += file_length(ja)
            ja_cat = ja_cat + ' ' + ja
            en_cat = en_cat + ' ' + en
            trans_cat = trans_cat + ' ' + trans

ja_cat = ja_cat + ' > ja_kitsu_cat'
en_cat = en_cat + ' > en_kitsu_cat'
trans_cat = trans_cat + ' > trans_kitsu_cat'

print 'writing ', i, ' lines'

os.system(ja_cat)
os.system(en_cat)
os.system(trans_cat)


# In[ ]:




# In[ ]:



