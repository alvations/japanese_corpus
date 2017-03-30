
# coding: utf-8

# In[84]:
from timeout import timeout
from pyunpack import Archive
from ffmpy import FFmpeg
import os
import time
from tqdm import tqdm
from difflib import SequenceMatcher
from joblib import Parallel, delayed

# In[101]:


def decompress_all(root):
    def decompress(target, destination):
        try:
            Archive(target).extractall(destination)
            os.system('rm "%s"' % target)
        except:
            pass

    for file in os.listdir(root):
        decompress(os.path.join(root, file), root)


def rm_all_spaces(root):
    def rename(f, dir=False):
        if f.find(" ") > 0:
            new = f.replace(" ", "-")
#            os.system('mv "%s" "%s"' % (f, new))
            os.rename(f, new)
            # TODO - refactor
            if dir:
                for subfile in os.listdir(new):
                    tgt = os.path.join(new, subfile)
                    os.system('mv "%s" "%s"' % (tgt, tgt.replace(' ', '-')))

    for root, dirs, files in os.walk(root):
        for name in dirs:
            try:
                rename(os.path.join(root, name), dir=True)
            except:
                os.system('rm -r "%s"' % os.path.join(root, name))

        for name in files:
            rename(os.path.join(root, name))

        
@timeout(30)
def convert_all(dir):
    def to_srt(target, destination):
        try:
            ff = FFmpeg(
                inputs={target: None},
                outputs={destination: None})
            ff.run()
v        except:
            pass

    def to_utf8(target):
        def get_charset():
            print 'WORKING ON', 'chardetect "%s"' % target
            output = os.popen('chardetect "%s"' % target).read()
            charset = output.split(':')[1].strip().split(' ')[0]
            return charset.upper()

        try:
            charset = get_charset()
            if 'UTF' not in charset:
                os.system('iconv -f %s -t UTF-8 "%s" > "%s"' % (charset, target, target + '.utf8'))
                if os.path.exists(target + '.utf8'):
                    os.system("rm '%s'" % target)
        except:
            pass

    for file in os.listdir(dir):
        to_utf8(os.path.join(dir, file))
    for file in os.listdir(dir):
        if not '.srt' in file:
            f = os.path.join(dir, file)
            to_srt(f, f + '.srt')

            
def rm_non_srt(dir):
    for file in os.listdir(dir):
        if not '.srt' in file:
            os.system('rm -r "%s"' % os.path.join(dir, file))
    
    
def flatten(dir):
    for root, dirs, files in os.walk(dir):
        for name in files:
            os.system('mv "%s" "%s"' % (os.path.join(root, name), dir))

    for root, dirs, files in os.walk(dir):
        for name in dirs:
            os.system('rm -r "%s"' % os.path.join(root, name))
      
@timeout(3)
def clean_of_nonsubs(dir):
    valid = [
        '.srt',
        '.ass',
        '.sub',
        '.lrc',
        '.sbv',
        '.cap',
        '.txt',
        '.idx',
        '.usf',
        '.jss',
        ]

    for file in os.listdir(dir):
        if os.path.splitext(file.lower())[1] not in valid:
            os.system('rm "%s"' % os.path.join(dir, file))

# In[1]:


def process_title_dir(dir):
    # decompmress
    try:
        print 'removing spaces...'
        rm_all_spaces(dir)
        print 'decompressing...'
        decompress_all(dir)
        print 'removing spaces from unpacked dirs/files...'
        rm_all_spaces(dir)

        # flatten
        print 'flatteining...'
        flatten(dir)

        # set permissions so that you can do stuff
        os.system('find %s -type f | xargs chmod u+rwx' % dir)

        print 'cleaning...'
        clean_of_nonsubs(dir)

        # convert all to utf8 srts
        print 'converting...'
        convert_all(dir)
    except:
        'ERROR on ', dir
    finally:
        # clean up
        rm_non_srt(dir)
        


# In[103]:

def process_dump(root, language='en'):
    """ Processes dump for one language. 
        Steps through each title dir, decompresses files within,
        and converts result to utf8/srt
    """
    os.system('find %s -type f -name "*.DS_Store" -delete' % root)
    Parallel(n_jobs=8)(delayed(process_title_dir)(os.path.join(root, title)) for title in tqdm(os.listdir(root)))

#    for title in os.listdir(root):
#        process_title_dir(os.path.join(root, title))
    

def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()


def get_joinable_titles(en_dump, ja_dump):
    en_titles = [x.lower() for x in os.listdir(en_dump)]
    ja_titles = [x.lower() for x  in os.listdir(ja_dump)]

    joined = []
    ja = []
    en = []
    for ja_title in tqdm(ja_titles):
        score, en_title = max( (similar(ja_title, en_title), en_title) for en_title in en_titles)
        if score > 0.81:
            en.append(en_title)
            ja.append(ja_title)
            joined.append( (ja_title, en_title) )
    return joined, en, ja


def rm_invalid(dump, valid):
    for dir in os.listdir(dump):
        if not dir.lower() in valid:
            os.system('rm -r "%s"' % os.path.join(dump, dir))


def join_dumps(en_dump, ja_dump, out_dump):
    os.system('find %s -type f | xargs chmod u+rwx' % en_dump)
    os.system('find %s -type f | xargs chmod u+rwx' % ja_dump)

    os.system('find %s -type f -name "*.DS_Store" -delete' % en_dump)    
    os.system('find %s -type f -name "*.DS_Store" -delete' % ja_dump)    

    rm_all_spaces(en_dump)
    rm_all_spaces(ja_dump)

    joined, valid_en, valid_ja = get_joinable_titles(en_dump, ja_dump)

    rm_invalid(en_dump, valid_en)
    rm_invalid(ja_dump, valid_ja)

    process_dump(en_dump)
    process_dump(ja_dump)

    for ja, en in joined:
        new_path = os.path.join(out_dump, en).replace(' ', '-')
        en_new = os.path.join(new_path, 'en')
        if not os.path.exists(en_new):
            os.makedirs(os.path.join(new_path, 'en'))
        ja_new = os.path.join(new_path, 'ja')
        if not os.path.exists(ja_new):
            os.makedirs(os.path.join(new_path, 'ja'))

        for f in os.listdir(os.path.join(en_dump, en)):
            os.system('mv "%s" "%s"' % (os.path.join(en_dump, en, f), os.path.join(new_path, 'en')))
        for f in os.listdir(os.path.join(ja_dump, ja)):
            os.system('mv "%s" "%s"' % (os.path.join(ja_dump, ja, f), os.path.join(new_path, 'ja')))
        



# In[ ]:

#process_dump('test')

join_dumps('/Users/rapigan/Documents/kitsunniko_raw/en_dump', 
           '/Users/rapigan/Documents/kitsunniko_raw/ja_dump',
           '/Users/rapigan/Documents/kitsunniko_raw/test')

# In[ ]:



