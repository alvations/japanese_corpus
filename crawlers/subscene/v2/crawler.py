"""
cd urls
split -l 1000 ja.txt ja_split.


"""
# coding: utf-8

# In[ ]:

import sys
from selenium import webdriver
import os
import uuid
import magic
from pyunpack import Archive
from ffmpy import FFmpeg
import re
import shutil
from joblib import Parallel, delayed
from tqdm import tqdm

# In[114]:

def file_length(f):
    return int(os.popen('wc -l %s' % f).read().strip().split()[0])


def download_subfile(url, name, dest):
    def get_dl_button(url):
        try:
            driver.get(url)
            return driver.find_element_by_id('downloadButton')
        except:
            print 'ERROR: cant get dl button ', url
            return False
            
    if not os.path.exists(dest):
        os.makedirs(dest)

    # download file
    elem = get_dl_button(url)
    if not elem:
        elem = get_dl_button(url)
    if not elem:
        print 'ERROR: couldnt get dl button x2', url
        return None
            
    dl_link = elem.get_attribute('href')
    dl_id = str(uuid.uuid4())
    target = os.path.join(dest, name + '-' + dl_id)
    os.system('wget -nc -P %s %s -O %s' % (dest, dl_link, target))

    return target


# In[115]:

def convert_all_to_srt(dir):
    def convert_to_srt(target, dest):
        ff = FFmpeg(
            inputs={target: None},
            outputs={dest: None})
        ff.run()

    for f in os.listdir(dir):
        try:
            f = os.path.join(dir, f)
            if '.srt' not in f:
                convert_to_srt(f, f + '.srt')
        except:
            pass
#            print 'ERROR: CONVERSION FAILURE ON', f


# In[116]:

def extract_archive(target, dest):
    # unzip if archive
    filetype = magic.from_file(target).lower()
    if 'zip' in filetype or 'rar' in filetype or 'tar' in filetype:
        Archive(target).extractall(dest)       
#        print 'EXTRACTED: ', target


# In[117]:

def dl_and_convert(dest, url, title):
    dlded_filepath = download_subfile(url, title, dest)
    if dlded_filepath:
        output = extract_archive(dlded_filepath, dest)
        convert_all_to_srt(dest)
        return True
    else:
        return False


# In[118]:

url_base = lambda url: re.findall("https://subscene.com/subtitles/(.*)/[japanese|english]", url)[0]
base_dir = 'out'

def process_url(url):
    try:
        print 'STARTING ', url
        title = url_base(url)
        dest = os.path.join(base_dir, title, 'ja')
        if dl_and_convert(dest, url, title):
            print 'SUCCESS ON', url
        else:
#            shutil.rmtree(os.path.join(base_dir, title))
            print 'FAILURE ON ', url
    except Exception as e:
        print 'MYSTERIOUS FAILURE ON: ', url, ' WITH EXCEPTION ', e


# In[ ]:

en_urls = open('urls/en.txt')
ja_urls = open(sys.argv[1])   # take from cli
driver = webdriver.Chrome()

url_base = lambda url: re.findall("https://subscene.com/subtitles/(.*)/[japanese|english]", url)[0]

base_dir = 'out'

#process_url('https://subscene.com/subtitles/weightlifting-fairy-kim-bok-joo-2016/japanese/1468874')

for url in tqdm(ja_urls, total=file_length(sys.argv[1])):
    process_url(url)

#Parallel(n_jobs=4)(delayed(process_url)(url) for url in ja_urls)


# In[ ]:



