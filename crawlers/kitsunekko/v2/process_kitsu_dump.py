
# coding: utf-8

# In[84]:

from pyunpack import Archive
from ffmpy import FFmpeg
import os
import time

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
            os.rename(f, new)
            # TODO - refactor
            if dir:
                for subfile in os.listdir(new):
                    tgt = os.path.join(new, subfile)
                    os.system('mv "%s" "%s"' % (tgt, tgt.replace(' ', '-')))

    for root, dirs, files in os.walk(root):
        for name in dirs:
            rename(os.path.join(root, name), dir=True)

        for name in files:
            rename(os.path.join(root, name))

        

def convert_all(dir):
    def to_srt(target, destination):
        ff = FFmpeg(
            inputs={target: None},
            outputs={destination: None})
        ff.run()
  
    def to_utf8(target):
        def get_charset():
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
      


# In[1]:

def process_title_dir(dir):
    # decompmress
    print 'removing spaces...'
    rm_all_spaces(dir)
    print 'decompressing...'
    decompress_all(dir)
    print 'removing spaces from unpacked dirs/files...'
    rm_all_spaces(dir)

    # flatten
    print 'flatteining...'
    flatten(dir)

    # convert all to utf8 srts
    print 'converting...'
    convert_all(dir)
    
    # clean up
    rm_non_srt(dir)
        


# In[103]:

def process_dump(root, language='en'):
    """ Processes dump for one language. 
        Steps through each title dir, decompresses files within,
        and converts result to utf8/srt
    """
    os.system('find %s -type f -name "*.DS_Store" -delete' % root)
    for title in os.listdir(root):
        process_title_dir(os.path.join(root, title))
    


# In[ ]:

process_dump('test')


# In[ ]:



