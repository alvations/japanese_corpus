

import os


for title in os.listdir('out'):
    for file in os.listdir(os.path.join('out', title, 'ja')):
        f = os.path.join('out', title, 'ja', file)
        if '.srt' not in f:
            os.system("rm '%s'" % f) 
#            print f
