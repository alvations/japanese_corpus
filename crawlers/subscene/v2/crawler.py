"""
cd urls
split -l 1000 ja.txt ja_split.


"""
# coding: utf-8

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


def extract_archive(target, dest):
    # unzip if archive
#    filetype = magic.from_file(target).lower()
#    if 'zip' in filetype or 'rar' in filetype or 'tar' in filetype:
    try:
        Archive(target).extractall(dest)
    except:
        pass
#        print 'EXTRACTED: ', target


def dl_and_convert(dest, url, title):
    dlded_filepath = download_subfile(url, title, dest)
    if dlded_filepath:
        output = extract_archive(dlded_filepath, dest)
        convert_all_to_srt(dest)
        return True
    else:
        return False


url_base = lambda url: re.findall("https://subscene.com/subtitles/(.*)/[japanese|english]", url)[0]
base_dir = 'out'

def process_url(url, language):
    try:
        print 'STARTING ', url
        title = url_base(url)
        if not os.path.exists(os.path.join(base_dir, title)) and language == 'en':
            print 'SKIPPED: not covered by ja'
            return
        dest = os.path.join(base_dir, title, language)
        if dl_and_convert(dest, url, title):
            print 'SUCCESS ON', url
        else:
#            shutil.rmtree(os.path.join(base_dir, title))
            print 'FAILURE ON ', url
    except Exception as e:
        print 'MYSTERIOUS FAILURE ON: ', url, ' WITH EXCEPTION ', e


urls = sys.argv[1]
url_f = open(urls)
language = 'ja' if 'ja' in urls else 'en'
url_base = lambda url: re.findall("https://subscene.com/subtitles/(.*)/[japanese|english]", url)[0]
driver = webdriver.Chrome()


for url in tqdm(url_f, total=file_length(sys.argv[1])):
    process_url(url, language)
    quit()
#Parallel(n_jobs=4)(delayed(process_url)(url) for url in ja_urls)





