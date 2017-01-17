"""
Many subtitle files have weird ass encodings like SHIFT-JIS, and aren't nessicarily 
  in srt format. This file should be able to handle pretty much any case, and make 
  a nicely packaged data structure for subs files.
"""
import sys
import os


class SubFile(object):
    
    def __init__(self, file_path):
        utf8_text = self.__convert_to_utf8(file_path)



    def __convert_to_utf8(self, fp):
        output = os.popen('chardetect %s' % fp).read()
        charset = output.split(':')[1].strip().split(' ')[0]      # ugly but chardetect's output is determanistic
        
        os.system('iconv -f %s -t UTF-8 %s > %s
